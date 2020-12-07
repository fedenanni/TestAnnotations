import os
import shutil
import json
from pathlib import Path

import random
import functools
from IPython.display import display, clear_output
from ipywidgets import Button, Dropdown, HTML, HBox, IntSlider, FloatSlider, Textarea, Output

# Annotation function. Code adapted from: https://github.com/agermanidis/pigeon/blob/master/pigeon/annotate.py
def annotate(examples,
             options=None,
             shuffle=False,
             include_skip=True,
             display_fn=display):
    """
    Build an interactive widget for annotating a list of input examples.
    Parameters
    ----------
    examples: list(any), list of items to annotate
    options: list(any) or tuple(start, end, [step]) or None
             if list: list of labels for binary classification task (Dropdown or Buttons)
             if tuple: range for regression task (IntSlider or FloatSlider)
             if None: arbitrary text input (TextArea)
    shuffle: bool, shuffle the examples before annotating
    include_skip: bool, include option to skip example while annotating
    display_fn: func, function for displaying an example to the user
    Returns
    -------
    annotations : list of tuples, list of annotated examples (example, label)
    """
    examples = list(examples)
    if shuffle:
        random.shuffle(examples)

    annotations = dict()
    current_index = -1

    def set_label_text():
        nonlocal count_label
        count_label.value = '{} examples annotated, example number {} out of {}'.format(
            len(annotations), current_index, len(examples)
        )

    def show_next():
        nonlocal current_index
        current_index += 1
        set_label_text()
        if current_index >= len(examples):
            for btn in buttons:
                btn.disabled = True
            print('Annotation done.')
            return
        if current_index <= 0:
            buttons[2].disabled = True
        elif current_index > 0:
            buttons[2].disabled = False
        with out:
            clear_output(wait=True)
            print(examples[current_index])

    def show_previous():
        nonlocal current_index
        current_index -= 1
        set_label_text()
        if current_index <= 0:
            buttons[2].disabled = True
        elif current_index > 0:
            buttons[2].disabled = False
        with out:
            clear_output(wait=True)
            print(examples[current_index])

    def add_annotation(annotation):
        annotation = annotation.strip()
        if annotation != "":
            if (annotation[0].lower() == "q" and annotation[1:].isnumeric()) or (annotation == "not_in_wikidata"):
                annotations[examples[current_index]] = annotation
                show_next()

    def skip(btn):
        show_next()

    def no_match(btn):
        add_annotation("not_in_wikidata")

    def back(btn):
        show_previous()

    count_label = HTML()
    set_label_text()
    display(count_label)

    buttons = []
    
    ta = Textarea()
    display(ta)
    btn = Button(description='submit')
    def on_click(btn):
        add_annotation(ta.value)
    btn.on_click(on_click)
    buttons.append(btn)

    btn = Button(description='not in wikidata')
    btn.on_click(no_match)
    buttons.append(btn)

    btn = Button(description='back')
    btn.on_click(back)
    buttons.append(btn)

    btn = Button(description='skip')
    btn.on_click(skip)
    buttons.append(btn)

    box = HBox(buttons)
    display(box)

    out = Output()
    display(out)

    show_next()

    return annotations


# Store annotations as a json file:
def store_annotations(annotations, data_to_annotate):
    name = os.getcwd().split("/")[2].split("jupyter-")[1]
    annotations_path = name + "_" + 'annotations.json'
    for x in annotations:
        data_to_annotate[x] = annotations[x]
    json.dump(data_to_annotate, open(annotations_path, 'w'))

    
# Load data:
def load_data():
    name = os.getcwd().split("/")[2].split("jupyter-")[1]
    annotations_path = name + "_" + 'annotations.json'
    
    # First time annotating: create your own annotation file:
    if not Path(annotations_path).exists():
        shutil.copyfile('samples_to_annotate.json', annotations_path)

    # Load annotation file:
    data_to_annotate = dict()
    with open(annotations_path) as f:
        data_to_annotate = json.load(f)
        
    return data_to_annotate