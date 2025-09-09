#!/usr/bin/env python3
"""
Basic usage example for miniworld-maze environments.

This is a minimal example showing how to create and interact with the environment.
"""

import gymnasium as gym
import miniworld_maze  # noqa: F401


def main():
    # Create environment using gymnasium registry
    env = gym.make("NineRooms-v0", obs_width=64, obs_height=64)
    obs, info = env.reset()

    # obs is a dictionary containing:
    # - 'observation': (64, 64, 3) RGB image array
    # - 'desired_goal': (64, 64, 3) RGB image of the goal state
    # - 'achieved_goal': (64, 64, 3) RGB image of the current state

    # Take a few random actions
    for step in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        print(f"Step {step + 1}: reward={reward:.3f}, terminated={terminated}")

        if terminated or truncated:
            obs, info = env.reset()

    env.close()
    print("Environment closed successfully!")


if __name__ == "__main__":
    main()
