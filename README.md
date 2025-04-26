# TetrisBot
**March 26, 2024**

In order to start this project, I've first started reading Reinforcement Learning: An Introduction. I plan to only go through the following chapters:  
  
Chapter 2: Multi-Armed Bandits  
Chapter 3: Finite Markov Decision Process  
Chapter 5: Monte Carlos Methods  
Chapter 6: Temporal-Difference Learning  
Chapter 8: Planning and Learning with Tabular Methods  
Chapter 9 & 10: On-Policy Prediction and Control with Approximation  
  
Currently, I've worked through chapter 2 and have done research into how I can implement this bot.

**March 27, 2024**

Although there are a lot of different gym environments, I wanted to be able to use this bot to participate in multiplayer games. This means that I will use PyAutoGUI in order to screenshot games online and simulate keystrokes. I finished chapter 3 and see that Tetris is an episodic task. However, it seems that the states that tetris could have is too large since with 20*10 blocks where each of them could be filled in or not, this means that there are about 2^200 different grid possibilities. Through skimming through research papers, I see that instead of calculating value functions for each states, we should use neural networks to approximate them which I happen to learn in chapter 6. I also found a helpful RL YouTube video on playing Snake that seems to take a similar approach.

**March 30, 2024**

I realized that training the model on a website where I have to take many screenshots is very computationally expensive as well as limiting. For now, I will train the model on my own environment I programmed since I couldn't find one where the model had access to the next couple pieces as well as the hold mechanic. 
