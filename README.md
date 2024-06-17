# ConvBench
Multi-turn visual conversation is an important ability of real-world AI assistants. However,  the related evaluation benchmark is missed. This paper presents ConvBench, a multi-turn conversation benchmark with hierarchical capabilities ablation evaluation for Large Vision-Language Models (LVLMs). ConvBench comprises 577 curated multi-turn conversations, encompassing 215 tasks. These tasks are broad and open-ended, which resemble real-world user behaviors. ConvBench progressively examines the LVLMs' perception, reasoning, and creativity capabilities in each conversation and can decouple these capabilities in evaluations and thus perform reliable error attribution. Besides, considering the diversity of open-ended questions, we introduce an efficient and reliable automatic evaluation framework. Experimental results reveal that ConvBench is a significant challenge for current LVLMs, even for GPT4v, which achieves only a 39.51 score. Besides, we have some insightful findings, such as the weak perception of LVLMs inhibits authentic strengths in reasoning and creation. We believe our design of hierarchical capabilities, decoupling capabilities evaluation, and multi-turn conversation can blaze a new trail in LVLMs evaluation.

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
