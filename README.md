# LLMs in Eduverse: LLM-Integrated English Educational Game in Metaverse

This project was originally introduced in the [2024 IEEE Global Conference on Consumer Electronics (GCCE 2024)](https://www.ieee-gcce.org/2024/index.html) and later extended in a journal publication.

This repository provides the **core API implementation** used in the following publications:

- **Conference paper (GCCE 2024)**  
  *LLMs in Eduverse: LLM-Integrated English Educational Game in Metaverse*  
  IEEE Global Conference on Consumer Electronics (GCCE 2024)

- **Journal paper**  
  *LLMs in EduGame: A Web-Based Interactive English Learning Game*  
  *(Accepted)*\
  **Protocol of user study conducted.**
  ![Protocol of user study]{ProtocolUS}

The API and codebase in this repository are shared across these works.  
The journal paper extends and builds upon the system introduced in the GCCE 2024 paper.

## Setup

### Install Dependencies

1. (optional) Creating conda environment

```
conda create -n metaguesser python=3.11
conda activate metaguesser
```

2. Install required packages

```
pip install -r requirements.txt
```

### Run Flask

```
flask run
```

## Citation
```bibtex
@inproceedings{plupattanakit2024llms,
  author={Plupattanakit, Kantinan and Suntichaikul, Pratch and Taveekitworachai, Pittawat and Thawonmas, Ruck and White, Jeremy and Sookhanaphibarn, Kingkarn and Choensawat, Worawat},
  booktitle={2024 IEEE 13th Global Conference on Consumer Electronics (GCCE)}, 
  title={LLMs in Eduverse: LLM-Integrated English Educational Game in Metaverse}, 
  year={2024},
  pages={257-258},
  keywords={Metaverse;Large language models;Semantics;Refining;Stochastic processes;Prototypes;Games;Consumer electronics;Large language models;Roblox;Metaverse;Word Guessing Game},
  doi={10.1109/GCCE62371.2024.10760474}}
```
