import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point, BLOCK_SIZE
from model import Linear_QNet, QTrainer
from helper import plot
import matplotlib as plt
import os

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games =0
        self.epsilon =0
        self.gamma=0.9
        self.memory=deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(21,256,3)        
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        model_path = "./model/u=1_k=1_rc=20/model_7.pth"
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path)
            model_state_dict = {
                'linear1.weight': checkpoint['linear1.weight'],
                'linear1.bias': checkpoint['linear1.bias'],
                'linear2.weight': checkpoint['linear2.weight'],
                'linear2.bias': checkpoint['linear2.bias']
                }
            self.model.load_state_dict(model_state_dict)


    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)

        point_l_bis = Point(head.x - 2*BLOCK_SIZE, head.y)
        point_r_bis = Point(head.x + 2*BLOCK_SIZE, head.y)
        point_u_bis = Point(head.x, head.y - 2*BLOCK_SIZE)
        point_d_bis = Point(head.x, head.y + 2*BLOCK_SIZE)

        point_l_ter = Point(head.x - 3*BLOCK_SIZE, head.y)
        point_r_ter = Point(head.x + 3*BLOCK_SIZE, head.y)
        point_u_ter = Point(head.x, head.y - 3*BLOCK_SIZE)
        point_d_ter = Point(head.x, head.y + 3*BLOCK_SIZE)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            # Danger straight bis
            (dir_r and game.is_collision(point_r_bis)) or 
            (dir_l and game.is_collision(point_l_bis)) or 
            (dir_u and game.is_collision(point_u_bis)) or 
            (dir_d and game.is_collision(point_d_bis)),

            # Danger right bis
            (dir_u and game.is_collision(point_r_bis)) or 
            (dir_d and game.is_collision(point_l_bis)) or 
            (dir_l and game.is_collision(point_u_bis)) or 
            (dir_r and game.is_collision(point_d_bis)),

            # Danger left bis
            (dir_d and game.is_collision(point_r_bis)) or 
            (dir_u and game.is_collision(point_l_bis)) or 
            (dir_r and game.is_collision(point_u_bis)) or 
            (dir_l and game.is_collision(point_d_bis)),
            
            # Danger straight ter
            (dir_r and game.is_collision(point_r_ter)) or 
            (dir_l and game.is_collision(point_l_ter)) or 
            (dir_u and game.is_collision(point_u_ter)) or 
            (dir_d and game.is_collision(point_d_ter)),

            # Danger right ter
            (dir_u and game.is_collision(point_r_ter)) or 
            (dir_d and game.is_collision(point_l_ter)) or 
            (dir_l and game.is_collision(point_u_ter)) or 
            (dir_r and game.is_collision(point_d_ter)),

            # Danger left ter
            (dir_d and game.is_collision(point_r_ter)) or 
            (dir_u and game.is_collision(point_l_ter)) or 
            (dir_r and game.is_collision(point_u_ter)) or 
            (dir_l and game.is_collision(point_d_ter)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.healthy_food.x < game.head.x,  # healthy food left
            game.healthy_food.x > game.head.x,  # healthy foodq
            game.healthy_food.y < game.head.y,  # healthy food up
            game.healthy_food.y > game.head.y,  # healthy food down

            game.drug_food.x < game.head.x,  # drug food left
            game.drug_food.x > game.head.x,  # drug food right
            game.drug_food.y < game.head.y,  # drug food up
            game.drug_food.y > game.head.y   # drug food down
            ]

        return np.array(state, dtype=int)
    
    def remember(self, state,action,reward,next_state, done):
        self.memory.append((state,action,reward,next_state, done))
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample=self.memory

        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states,actions,rewards,next_states,dones)

    def train_short_memory(self, state,action,reward,next_state, done):
        self.trainer.train_step(state,action,reward,next_state, done)


    def get_action(self, state):
        #random moves
        self.epsilon = 80 - self.n_games
        final_move =[0,0,0]
        # if random.randint(0,200)<self.epsilon:
        #    move=random.randint(0,2)
        #    final_move[move]=1
        # else:
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        return final_move

def train(essai, ittération):
    for i in range(essai):
        save_path = f"./results/final/u=1_k=1_rc=20"
        model_path = "/final/u=1_k=1_rc=20"
        plot_scores=[]
        plot_mean_scores=[]
        plot_mean_healthy_seed=[]
        plot_mean_drug_seed=[]
        total_score=0
        total_healthy_seed=0
        total_drug_seed=0
        record=0
        agent=Agent()
        game=SnakeGameAI()
        while agent.n_games < ittération + 1:
            state_old = agent.get_state(game)

            final_move = agent.get_action(state_old)

            reward,done,score,healthy_seed_consumed,drug_seed_consumed,len = game.play_step(final_move)

            state_new=agent.get_state(game)

            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                game.reset()
                agent.n_games+=1
                agent.train_long_memory()

                if score > record:
                    record=score
                    agent.model.save(model_path, filename=f"model_{i}.pth")
                    
                
                print("Game", agent.n_games, 'Score',score, 'Healthy seed',healthy_seed_consumed, "Drug seed",drug_seed_consumed, 'Record', record, 'len', len)
                plot_scores.append(score)
                total_score+=score
                total_healthy_seed+=healthy_seed_consumed
                total_drug_seed+=drug_seed_consumed
                mean_score = total_score/agent.n_games
                mean_healthy_seed = total_healthy_seed/agent.n_games
                mean_drug_seed = total_drug_seed/agent.n_games
                plot_mean_scores.append(mean_score)
                plot_mean_healthy_seed.append(mean_healthy_seed)
                plot_mean_drug_seed.append(mean_drug_seed)
                plot(plot_scores, plot_mean_scores, plot_mean_healthy_seed, plot_mean_drug_seed)
                if agent.n_games == ittération:
                    plot(plot_scores, plot_mean_scores, plot_mean_healthy_seed, plot_mean_drug_seed, save_path, f"/essai_{i}")

if __name__=='__main__':
    train(1,100)
    
