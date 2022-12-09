'''
Copyright 2022 The Microsoft DeepSpeed Team
'''
import torch
from torch.nn.parameter import Parameter
from ..policy import TransformerPolicy


class HFGPTJLayerPolicy(TransformerPolicy):
    _orig_layer_class = None

    def __init__(self, client_module, inference=True):
        super().__init__(inference, scale_attention=True)
        self.client_module = client_module
        try:
            import transformers
            HFGPTJLayerPolicy._orig_layer_class = transformers.models.gptj.modeling_gptj.GPTJBlock
        except:
            HFGPTJLayerPolicy._orig_layer_class = None

    def get_hidden_heads(self):
        return self.client_module.attn.q_proj.weight.shape[1], \
                self.client_module.attn.num_attention_heads

    def attention(self):
        qw = self.client_module.attn.q_proj.weight
        kw = self.client_module.attn.k_proj.weight
        vw = self.client_module.attn.v_proj.weight

        qkvw = Parameter(torch.cat((qw, kw, vw), dim=0), requires_grad=False)

        return qkvw, \
               None, \
               self.client_module.attn.out_proj.weight, \
               None,

    def mlp(self):
        return self.client_module.mlp.fc_in.weight, \
               self.client_module.mlp.fc_in.bias, \
               self.client_module.mlp.fc_out.weight, \
               self.client_module.mlp.fc_out.bias

    def layernorm(self):
        return None, \
               None, \
               self.client_module.ln_1.weight, \
               self.client_module.ln_1.bias

    def get_param_names(self):
        return 'attn.q_proj.weight', \
               'attn.k_proj.weight', \
               'attn.v_proj.weight', \
               'attn.out_proj.weight', \
               'mlp.fc_in.weight', \
               'mlp.fc_in.bias', \
               'mlp.fc_out.weight', \
               'mlp.fc_out.bias', \
               'ln_1.weight', \
               'ln_1.bias', \
               self.use_load_prefix, \
               self.split_qkv
