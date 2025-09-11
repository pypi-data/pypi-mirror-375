from abc import abstractmethod, ABC
import re
from typing import Dict

import torch
import torch.nn as nn
from src.output_tools.save_run import SaveRun


class NNTrainerAbstract(ABC):
    def __init__(self, model, optimizer, loss_fn, device, scheduler=None):
        self._model = model
        self._optimizer = optimizer
        self._loss_fn = loss_fn
        self._device = device
        self._scheduler = scheduler

    @abstractmethod
    def train_step(self, batch):
        """
        Perform a single training step. Must be implemented by subclasses.
        """
        raise NotImplementedError
    
    @abstractmethod
    def evaluate(self, dataloader):
        """
        Evaluate the model on a validation or test set. Must be implemented by subclasses.
        """
        raise NotImplementedError

    def train(self, dataloader, epochs, step_params:Dict, save_run: SaveRun = None, val_loader=None, test_loader=None):
        """
        Generic training loop. Assumes `train_step` always returns a dictionary of losses.
        Returns:
            list: A list of average losses for each epoch.
        """
        epoch_losses = []

        for epoch in range(epochs):
            self._model.train()
            loss_dict = {}

            for batch in dataloader:
                batch_loss = self.train_step(batch, step_params)

                # Accumulate losses
                for key, value in batch_loss.items():
                    loss_dict[key] = loss_dict.get(key, 0) + value.item()

            # Average and print losses
            for key in loss_dict:
                loss_dict[key] /= len(dataloader)
                if save_run:
                    save_run.log_metric(key, loss_dict[key])
            # Optional evaluation on val/test
            val_loss = None
            test_loss = None
            if val_loader is not None:
                val_loss = self.evaluate(val_loader)
                loss_dict["val_loss"] = val_loss
                if save_run:
                    save_run.log_metric("val_loss", val_loss)
            if test_loader is not None:
                test_loss = self.evaluate(test_loader)
                loss_dict["test_loss"] = test_loss
                if save_run:
                    save_run.log_metric("test_loss", test_loss)
                    
            print(f"Epoch {epoch + 1} | " + " | ".join(f"{key}: {value:.4f}" for key, value in loss_dict.items()))
            epoch_losses.append(loss_dict)

            if self._scheduler:
                self._scheduler.step(loss_dict.get("loss", 0))

        return epoch_losses
    
    def get_model(self):
        """
        Retrieve the trained model.
        """
        return self._model

class TransformerTrainer(NNTrainerAbstract):
    def train_step(self, batch, step_params:Dict):
        """
        Perform a single training step for sequence models.

        Args:
            batch (tuple): A batch of data (inputs, targets).
        Returns:
            dict: A dictionary containing the computed loss for the batch.
        """
        # Unpack the batch
        batch_inputs, batch_targets = batch
        batch_inputs, batch_targets = batch_inputs.to(self._device), batch_targets.to(self._device)

        # Zero the gradients
        self._optimizer.zero_grad()

        # Create src_mask based on sequence lengths
        src_lengths = [t.size(0) for t in batch_inputs.unbind()]
        max_len = max(src_lengths)
        src_mask = self._model.generate_square_subsequent_mask(max_len).to(self._device)

        # Forward pass
        output = self._model(batch_inputs, src_mask)

        # Calculate loss
        loss = 0
        batch_size = len(src_lengths)
        output_list = [output[i, :src_lengths[i]] for i in range(batch_size)]
        target_list = [batch_targets[i] for i in range(batch_size)]

        for out_seq, target_seq in zip(output_list, target_list):
            loss += self._loss_fn(out_seq, target_seq)

        loss = loss / batch_size  # Average loss

        # Backward pass and optimization
        loss.backward()
        if step_params["clip_gradients"]:
            torch.nn.utils.clip_grad_norm_(self._model.parameters(), 1.0)
        self._optimizer.step()

        return {"loss": loss}
    
    
    def evaluate(self, dataloader):
        """
        Compute average loss over a dataloader without gradient updates.
        """
        self._model.eval()
        total_loss = 0.0
        num_batches = 0
        with torch.no_grad():
            for batch in dataloader:
                batch_inputs, batch_targets = batch
                batch_inputs, batch_targets = batch_inputs.to(self._device), batch_targets.to(self._device)

                src_lengths = [t.size(0) for t in batch_inputs.unbind()]
                max_len = max(src_lengths)
                src_mask = self._model.generate_square_subsequent_mask(max_len).to(self._device)

                output = self._model(batch_inputs, src_mask)

                loss = 0.0
                batch_size = len(src_lengths)
                output_list = [output[i, :src_lengths[i]] for i in range(batch_size)]
                target_list = [batch_targets[i] for i in range(batch_size)]
                for out_seq, target_seq in zip(output_list, target_list):
                    loss += self._loss_fn(out_seq, target_seq)
                loss = loss / batch_size

                total_loss += loss.item()
                num_batches += 1
        self._model.train()
        return total_loss / max(1, num_batches)
    
    


class TransformerFineTuneTrainer(TransformerTrainer):
    def __init__(self, model, optimizer, loss_fn, device, scheduler=None, freeze_base=True):
        super().__init__(model, optimizer, loss_fn, device, scheduler)
        if freeze_base:
            for param in self._model.base_model.parameters():
                param.requires_grad = False
                
                
                
    def train_step(self, batch, step_params:Dict):
        pass
    
    def add_lora_layers(self, r, alpha, freeze_non_lora_layers=True, target_regex=None, qkv: str = "qvk"):
        """
        Add LoRA adapters only to selected paths (query/key/value) of nn.MultiheadAttention layers.

        Args:
            base_model (nn.Module): The base model to modify (must contain nn.MultiheadAttention layers).
            r (int): Rank of the low-rank matrices.
            alpha (float): Scaling factor for the low-rank matrices.
            freeze_non_lora_layers (bool): Whether to freeze all non-LoRA parameters.
            target_regex (str, optional): Regex to select which attention module names to modify.
                                        If None, modules with names containing typical attention tokens are targeted.
            qkv (str): Any combination of 'q', 'k', 'v' (e.g., "qv", "q", "qvk") specifying
                    which inputs to adapt with LoRA. Order is irrelevant.
        """
        target_pattern = re.compile(target_regex) if target_regex else None
        
        targets = set(ch for ch in qkv.lower() if ch in {"q", "k", "v"})

        def is_attention_name(name: str) -> bool:
            if target_pattern:
                return bool(target_pattern.search(name))
            # Default heuristic if no regex supplied
            attn_tokens = ("attn", "attention", "self_attn", "self_attention")
            return any(tok in name for tok in attn_tokens)

        # Collect nn.MultiheadAttention modules to wrap
        attn_modules_to_wrap = [
            (name, module)
            for name, module in self._model.named_modules()
            if isinstance(module, nn.MultiheadAttention)
            and is_attention_name(name)
            and not hasattr(module, "_is_lora_qkv_modified")
        ]

        # Freeze non-LoRA params
        if freeze_non_lora_layers:
            for _, p in self._model.named_parameters():
                p.requires_grad = False

        # Wrap each attention module
        for name, attn in attn_modules_to_wrap:
            self._wrap_mha_with_qkv_lora(attn, name, r, alpha, targets)
    
    
    
    def _wrap_mha_with_qkv_lora(self, attn_module: nn.MultiheadAttention, name: str, r: int, alpha: float, targets: set):
        """
        Wrap nn.MultiheadAttention.forward to add LoRA deltas only to selected inputs (Q/K/V).
        This does not alter internal projection weights; it adapts inputs directly.
        """
        # Determine device/dtype from existing parameters
        try:
            ref_param = next(attn_module.parameters())
            device, dtype = ref_param.device, ref_param.dtype
        except StopIteration:
            device, dtype = torch.device("cpu"), torch.float32

        embed_dim = attn_module.embed_dim
        scaling = alpha / r

        # Prepare LoRA adapters for selected targets
        def make_pair(prefix: str):
            down = nn.Linear(embed_dim, r, bias=False).to(device=device, dtype=dtype)
            up = nn.Linear(r, embed_dim, bias=False).to(device=device, dtype=dtype)
            down.custom_name = f"{name}.{prefix}_lora_down"
            up.custom_name = f"{name}.{prefix}_lora_up"
            # Init so initial effect ~0
            nn.init.zeros_(down.weight)
            nn.init.normal_(up.weight, mean=0.0, std=0.01)
            # Trainable
            down.weight.requires_grad = True
            up.weight.requires_grad = True
            return down, up

        if "q" in targets:
            attn_module.q_lora_down, attn_module.q_lora_up = make_pair("q")
        if "k" in targets:
            attn_module.k_lora_down, attn_module.k_lora_up = make_pair("k")
        if "v" in targets:
            attn_module.v_lora_down, attn_module.v_lora_up = make_pair("v")

        attn_module._lora_scaling = scaling
        attn_module._is_lora_qkv_modified = True

        original_forward = attn_module.forward

        def modified_forward(query, key, value, *args, **kwargs):
            # Apply LoRA only where requested, along last dim (embed_dim)
            if "q" in targets:
                q_delta = attn_module.q_lora_up(attn_module.q_lora_down(query)) * attn_module._lora_scaling
                query = query + q_delta
            if "k" in targets:
                k_delta = attn_module.k_lora_up(attn_module.k_lora_down(key)) * attn_module._lora_scaling
                key = key + k_delta
            if "v" in targets:
                v_delta = attn_module.v_lora_up(attn_module.v_lora_down(value)) * attn_module._lora_scaling
                value = value + v_delta
            return original_forward(query, key, value, *args, **kwargs)

        attn_module.forward = modified_forward
    
    