# -*- coding: utf-8 -*-
# @Time    : 2022/6/15 下午5:51
# @Author  : caden1225
# @File    : MemoryDecoder_get.py
# @Description : 说明一下
from projects.blenderbot2.agents.sub_modules import MemoryDecoder
import json
import torch
from parlai.utils.torch import padded_tensor as padded_tensor
from parlai.utils.torch import padded_3d

def set_memory_decoder_vec(decoder, lines):
    def tokenize_memory_decoder_input(decoder, input: str):
        return decoder.tokenize_input(input)

    memory_decoder_vec = [torch.Tensor([tokenize_memory_decoder_input(decoder, str(i))]) for i in lines]
    return memory_decoder_vec

def set_batch_memory_decoder_vec(memory_decoder_vec):
    batch = {}
    memory_dec_toks = []
    num_memory_dec_toks = []
    p_sum_vecs, _lens = padded_tensor(memory_decoder_vec, pad_idx=0)

    memory_dec_toks.append(p_sum_vecs)
    num_memory_dec_toks.append(len(memory_decoder_vec))

    batch['memory_decoder_vec'] = padded_3d(memory_dec_toks)
    batch['num_memory_decoder_vecs'] = torch.LongTensor(num_memory_dec_toks)
    return batch

def generate_memores(decoder, batch):
    memories = decoder.generate_memories(
        batch['memory_decoder_vec'], batch['num_memory_decoder_vecs']
    )
    return memories

def main():
    opt = json.load(open('/data/for_libo/temp_opt.opt', 'r'))
    print(opt)
    decoder = MemoryDecoder(opt=opt)

    import pandas as pd

    raw_df = pd.read_excel('/data/for_libo/1wdata_test.xlsx')
    input_list = raw_df['英文'].to_list()

    res = []
    memory_decoder_vec_lines = set_memory_decoder_vec(decoder, input_list)
    for memory_decoder_vec in memory_decoder_vec_lines:
        batch = set_batch_memory_decoder_vec(memory_decoder_vec)
        res.append(generate_memores(decoder, batch))

    raw_df['memories'] = res
    raw_df.to_excel('/data/for_libo/1wdata_result.xlsx')
if __name__=="__main__":
    main()
