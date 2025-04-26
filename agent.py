import torch.optim as optim
from model import DQN as model
import tetris as env
import random
import torch
import torch.nn.functional as F

class Agent:
    def __init__(self):
        self.online_net = model(230,7)
        self.target_net = model(230,7)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.epsilon = 1.0 # Chance you explore
        self.discount = 0.99
        self.epsilonDecay = 0.995
        self.memory = []
        self.env = env.Tetris()
        self.optimizer = optim.Adam(self.online_net.parameters())
    
    def selectAction(self, state):
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        if random.random() <= self.epsilon:
            return random.randint(0,6)
        with torch.no_grad():
            q_values = self.online_net(state_tensor)
            best_action = int(torch.argmax(q_values[0]).item())
        return best_action


    def train(self):
        for i in range(1000):
            ep_reward = 0
            self.env.reset()
            while True:
                oldState = self.env.getState()
                action = self.selectAction(oldState)
                newState, reward, done = self.env.play_step(action)
                ep_reward += reward
                if done:
                    break
                
                self.memory.append((oldState, reward, action, newState, done))

                if len(self.memory) >= 64:
                    batch = random.sample(self.memory, 64)

                    for state, r, a, next_state, done in batch:
                        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                        next_state = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)

                        q_values = self.online_net(state)
                        q_value = q_values[0, a]

                        with torch.no_grad():
                            next_q_values = self.target_net(next_state)
                            max_next_q = torch.max(next_q_values)
                            target = r if done else r + self.discount * max_next_q

                        loss = F.mse_loss(q_value, target)

                        self.optimizer.zero_grad()
                        loss.backward()
                        self.optimizer.step()

            if i % 10 == 0:
                self.target_net.load_state_dict(self.online_net.state_dict())


            self.epsilon *= self.epsilonDecay if self.epsilon > 0.1 else 1
            print(f"Episode {i} | Reward: {ep_reward} | Epsilon: {self.epsilon:.3f}")

    
if __name__ == "__main__":
    agent = Agent()
    agent.train()