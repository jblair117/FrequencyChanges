# Branching Frequency Detection Tool with Visual Analytics

## Purpose

The purpose of this system is to provide valuable information to a business process by detecting drift points and using branching frequencies to see points in time where we can evaluate critical details such as 

- where resources should be further utilised, or
- process that should be entirely changed to fit actual events rather than how the events are expected to occur.

A real world application use is in a hospital triage process, where if the proportion of emergency patients is found to be increasing, more resources can be sent to the emergency department to optimise the process.

## Article

The system utilises the algorithm from the codebase below:

https://github.com/bearlu1996/FrequencyChange

This codebase originates from the article below:

Lu, Y., Chen, Q., & Poon, S. (2021). Detecting and Understanding Branching Frequency Changes in Process Models. arXiv preprint [arXiv:2103.07052](https://arxiv.org/abs/2103.10742).

## Access to Site

The site can be accessed by the link below:

https://process-mining-zkathz2wkq-ts.a.run.app/

## Requirements

The site requires uploading **1 .pnml** file and **1 .xes** file which are a petri-net model and event log respectively. The petri-net model **must** be sound and it is preferred that the event log is generated via process discovery from the **.pnml** file that the user wishes the system to analyse.
