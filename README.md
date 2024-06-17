# ConvBench
<p align="left">
  <a href="https://arxiv.org/abs/2403.20194"><b>arXiv Paper</b></a> |
</p>


This repository is the official implementation of [ConvBench](https://arxiv.org/abs/2403.20194).

> [ConvBench: A Multi-Turn Conversation Evaluation Benchmark with Hierarchical Ablation Capability for Large Vision-Language Models](https://arxiv.org/abs/2403.20194)  
> Shuo Liu, Kaining Ying, Hao Zhang, Yue Yang, Yuqi Lin, Tianle Zhang, Chuanhao Li, Yu Qiao, Ping Luo, Wenqi Shao<sup>\#</sup>, Kaipeng Zhang<sup>\#</sup>  
> <sup>\#</sup> WS (shaowenqi@pjlab.org.cn) and KZ (zhangkaipeng@pjlab.org.cn) are correponding authors. 


# Introduction
Multi-turn visual conversation is an important ability of real-world AI assistants. However,  the related evaluation benchmark is missed. This paper presents ConvBench, a multi-turn conversation benchmark with hierarchical capabilities ablation evaluation for Large Vision-Language Models (LVLMs). ConvBench comprises 577 curated multi-turn conversations, encompassing 215 tasks. These tasks are broad and open-ended, which resemble real-world user behaviors. ConvBench progressively examines the LVLMs' perception, reasoning, and creativity capabilities in each conversation and can decouple these capabilities in evaluations and thus perform reliable error attribution. Besides, considering the diversity of open-ended questions, we introduce an efficient and reliable automatic evaluation framework. Experimental results reveal that ConvBench is a significant challenge for current LVLMs, even for GPT4v, which achieves only a 39.51 score. Besides, we have some insightful findings, such as the weak perception of LVLMs inhibits authentic strengths in reasoning and creation. We believe our design of hierarchical capabilities, decoupling capabilities evaluation, and multi-turn conversation can blaze a new trail in LVLMs evaluation.

![image](https://github.com/shirlyliu64/ConvBench/blob/main/assets/convbench_detail.png)

# Main Findings
Based on our benchmark, we conducted a series of experiments. The main findings are summarized as follows:

* The most advanced LVLMs (e.g. GPT4V) still struggle to solve the cahllenge provided by ConvBench
* The novel hierarchical ablation evaluations of ConvBench conclude that the weakness of ``OCR'', ``Fine-grained'', and ``Spatial'' perception of current LVLMs may inhibit the performance of the next reasoning and creation tasks.
* The weakness of LVLMs' reasoning capability demanding ``Professional Knowledge'', ``Emotional Intelligence'', ``Imagination'', and ``Sense of Space'' may hinder the performance of the next creation.
* The performances across different tasks of different LVLMs show a similar distribution, which suggests the development of current LVLMs is synchronous.
* Performance improves as the language model size of LVLM increases.
* A declined performance between the first turn and subsequent turns shows that LVLMs tend to generate comprehension biases as the multi-turn conversation progresses or forget the information of previous turns.
* The high-quality dialogue history provides important guidance to the LVLMs' responses and plays an important role in in-context learning examples.

# Experimental Results
![image](https://github.com/shirlyliu64/ConvBench/blob/main/assets/leaderboard.png)

The performances across different tasks of different LVLMs show a similar distribution, which suggests the development of current LVLMs is synchronous.

![image](https://github.com/shirlyliu64/ConvBench/blob/main/assets/task_evalutation.png)



# Acknowledgement
ConvBench is build upon the documents from [VisIT-Bench](https://github.com/mlfoundations/VisIT-Bench/tree/main) which is a robust benchmark for diverse real-life vision-language instructions. [VLMEvalKit](https://github.com/open-compass/VLMEvalKit) provides useful out-of-box tools and implements many adavanced LVLMs. Thanks for their selfless dedication.

# License
The new contributions of our dataset (e.g., the instructions, reference outputs, model ranking annotations, etc.) are licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). For the images that were used are same with those from [VisIT-Bench](https://github.com/mlfoundations/VisIT-Bench/tree/main), please refer to the public license attached to each individual image in the "public_images_metadata" field in the dataset sheets in [VisIT-Bench](https://github.com/mlfoundations/VisIT-Bench/tree/main).


# Citation
Please cite the following paper if you feel this repo useful to your research

```ruby
@article{Liu2024ConvBenchAM,
  title={ConvBench: A Multi-Turn Conversation Evaluation Benchmark with Hierarchical Capability for Large Vision-Language Models},
  author={Shuo Liu and Kaining Ying and Hao Zhang and Yue Yang and Yuqi Lin and Tianle Zhang and Chuanhao Li and Yu Qiao and Ping Luo and Wenqi Shao and Kaipeng Zhang},
  journal={ArXiv},
  year={2024},
  volume={abs/2403.20194},
  url={https://api.semanticscholar.org/CorpusID:268793453}
}
```
