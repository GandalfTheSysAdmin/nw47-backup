"""
topics.py

This module defines the `topic` class, which encapsulates information about a Discord topic.
Each topic object stores the topic ID and the topic name, and provides methods
to retrieve these details.

Author: GandalfTheSysAdmin
Date: 2024-08-31

Class:
    - topic: Stores topic-specific information like topic ID and name.

Usage:
    - Import the `topic` class in your script.
    - Create an instance of `topic` by passing the topic ID and name as arguments.

Example:
    from topics import topic
    topic = topic('1166422305069600870', 'general')

License: MIT License
"""

TOPICS = {
	'automation': '1152724568788713502',
	'breeding': '1161819028050948097',
	'cannabis-info-files': '1152724428170481744',
	'concentrates': '1153031967525326918',
	'edibles': '1153032189437542561',
	'podcast-suggestions': '1157401550050820136',
	'gaming': '1153031305257299991',
	'indoor-growing': '1152724355432853534',
	'pest-management': '1153031886583644173',
	'propagation-tech': '1153034060264902656',
    'science': '1166422305069600870',
	'lighting': '1153033640519946414',
	'natural-farming': '1152724626368122971',
	'strains': '1153233929411768370', 
	'wall-street-bets': '1153043405123891281', 
	'everything-organics': '1245817702086475826',
    # Add more topics here
}


class Topic:
    def __init__(self, topic_id, name):
        self.topic_id = topic_id
        self.name = name

    def __repr__(self):
        return f"topic(name='{self.name}', topic_id='{self.topic_id}')"

    def get_topic_id(self):
        return self.topic_id

    def get_topic_name(self):
        return self.name

