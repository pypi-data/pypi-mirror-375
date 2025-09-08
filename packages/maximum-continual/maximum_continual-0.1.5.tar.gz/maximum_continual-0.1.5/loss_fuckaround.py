"""Efficient batch training with DeepSpeed optimization"""
import torch
from transformers import Trainer, TrainingArguments
from peft import PeftModel, LoraConfig, get_peft_model, TaskType
from torch.utils.data import Dataset
import json
import os
from maximum_continual.types import MessageT
with open("response.json", "r") as f:
    response = [MessageT(**message) for message in json.load(f)['messages']]
batch_messages = [([msg.to_transformers_message() for msg in response], 1.0)]
tokenizer = self.tokenizer
base_model_instance = self.base_model
model_info_backend = ModalModelInfoBackend(model_id, lora_vol_path=LORA_PATH)
# Custom dataset for reward-weighted training
class RewardWeightedDataset(Dataset):
    def __init__(self, batch_messages, tokenizer, max_length=2048):
        self.data = []
        for messages, reward in batch_messages:
            formatted_text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
            tokenized = tokenizer(
                formatted_text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_tensors="pt"
            )
            self.data.append({
                'input_ids': tokenized['input_ids'].squeeze(),
                'attention_mask': tokenized['attention_mask'].squeeze(),
                'reward': reward,
                'length': tokenized['input_ids'].shape[1]
            })
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]



# Custom trainer with reward-weighted loss
class RewardWeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        rewards = inputs.get("rewards")
        print(f"Rewards: {rewards}", labels)
        # Ensure rewards tensor is on the right device and has gradients enabled
        if rewards is not None:
            device = next(model.parameters()).device
            rewards = rewards.to(device).detach()  # Detach rewards to avoid gradient issues
        with ope
        outputs = model(**{k: v for k, v in inputs.items() if k not in ['rewards']})
        print("Output shape: ", outputs.logits.shape)
        mini_loss = (outputs.logits/outputs.logits.detach()).mean(dim=-1) * rewards
        print(f"Mini loss: {mini_loss}")
        if labels is not None:
            shift_logits = outputs.logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            
            # Compute per-token loss
            loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
            token_losses = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1)
            ).view(shift_labels.size())  # [batch_size, seq_len-1]
            print(f"Token losses: {token_losses}")
            # Apply reward weighting
            if rewards is not None:
                # Expand rewards to match token dimensions
                reward_weights = rewards.unsqueeze(1).expand_as(token_losses).detach()
                weighted_losses = token_losses * reward_weights
            else:
                weighted_losses = token_losses
            print(f"Weighted losses: {weighted_losses}")
            # Mask out padded tokens
            attention_mask = inputs.get('attention_mask')
            if attention_mask is not None:
                mask = attention_mask[..., 1:].float()  # Shift mask to match labels
                weighted_losses = weighted_losses * mask
                valid_tokens = mask.sum()
                if valid_tokens > 0:
                    loss = weighted_losses.sum() / valid_tokens
                else:
                    loss = weighted_losses.sum()  # Fallback if no valid tokens
            else:
                loss = weighted_losses.mean()
            print(f"Loss: {loss}")
            # Debug: Check if loss requires grad
            if not loss.requires_grad:
                print(f"WARNING: Loss does not require gradients! Loss shape: {loss.shape}")
                print(f"Model has trainable params: {any(p.requires_grad for p in model.parameters())}")
            
        else:
            loss = outputs.loss

        return (loss, outputs) if return_outputs else loss

# Load model and tokenizer
lora_info = model_info_backend.fetch_current_step()

if lora_info is None:
    initial_lora_info = model_info_backend.fetch_initial_step()
    base_model = initial_lora_info.base_model
else:
    base_model = lora_info.base_model


# Custom data collator for reward weighting
def reward_weighted_collate_fn(batch):
    # Pad sequences to same length
    max_len = max(item['length'] for item in batch)
    
    input_ids = []
    attention_masks = []
    rewards = []
    
    for item in batch:
        # Pad input_ids and attention_mask
        pad_length = max_len - item['length']
        if pad_length > 0:
            input_ids.append(torch.cat([
                item['input_ids'], 
                torch.full((pad_length,), tokenizer.pad_token_id)
            ]))
            attention_masks.append(torch.cat([
                item['attention_mask'],
                torch.zeros(pad_length)
            ]))
        else:
            input_ids.append(item['input_ids'])
            attention_masks.append(item['attention_mask'])
        
        rewards.append(item['reward'])
    
    return {
        'input_ids': torch.stack(input_ids),
        'attention_mask': torch.stack(attention_masks),
        'labels': torch.stack(input_ids),  # For causal LM, labels = input_ids
        'rewards': torch.tensor(rewards, dtype=torch.float32)
    }

# Load model with more efficient configuration for DeepSpeed

# Load or create LoRA
if lora_info is not None and os.path.exists(lora_info.full_lora_path):
    model = PeftModel.from_pretrained(base_model_instance, lora_info.full_lora_path)
    print(f"Loaded LoRA from: {lora_info.full_lora_path}")
else:
    lora_config = LoraConfig(
        r=32,
        lora_alpha=32,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            # Removed MLP modules for VLLM compatibility
            # "gate_proj", "up_proj", "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(base_model_instance, lora_config)
    print(f"Created new LoRA model: {base_model}")
    print(f"LoRA target modules (VLLM-compatible): {lora_config.target_modules}")

# Ensure model is in training mode and LoRA parameters require gradients
model.train()
# Prepare dataset
dataset = RewardWeightedDataset(batch_messages, tokenizer)



# Training arguments
training_args = TrainingArguments(
    output_dir="./tmp_training",
    num_train_epochs=1,
    per_device_train_batch_size=min(4, len(batch_messages)),
    gradient_accumulation_steps=max(1, len(batch_messages) // 4),
    learning_rate=learning_rate,
    warmup_steps=0,
    logging_steps=1,
    save_steps=10,
    save_total_limit=0,
    prediction_loss_only=True,
    remove_unused_columns=False,
    dataloader_drop_last=False,
    gradient_checkpointing=True,
    report_to=None,  # Disable wandb/tensorboard
)

# Initialize trainer
trainer = RewardWeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=reward_weighted_collate_fn,
    tokenizer=tokenizer,
)

# Train
print(f"Training on {len(batch_messages)} conversations")
trainer.train()

