#! /usr/bin/python
# coding: utf-8

class QueueEmptyError(Exception):
    """
    キューが空の時の例外
    """
    def __init__(self):
        pass
    def __str__(self):
        return "Queue is empty!!"

class QueueNotOverYetError(Exception):
    """キューが終了していないときの例外"""
    def __init__(self):
        pass
    def __str__(self):
        return "Task is not finished."

