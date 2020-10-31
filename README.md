A cookbook, written in Python
=============================

This module (and associated `pycook.py` utility) implement a simple cookbook
creation tool.  The objective is to make it as simple and ergonomic to use as
possible from the perspective of someone familiar with Markdown or
reStructuredText.  The recipes are represented as a directory tree of YAML
files which you can manage with your favorite version-control tool.  PyCook
turns these YAML files into one of a few output formats:

 - A searchable HTML cookbook (built using Sphinx)
 - A PDF cookbook (uses LaTeX)
 - A PDF of 4x6 recipe cards printable on Avery 5389 templates

## Recipe format

Recipes are described using an ergonomic YAML-based format.  The primary
objective of this format is to be as easily for a human to read/write as
possible while still retaining enough semantic information that PyCook can
massage it into the different output formats. As an example, this is the YAML
file for a pretty good pancake recipe:

```yaml
name: Jason's Café Pancakes
from: Jason Ekstrand
url: https://github.com/jekstrand/pycook

ingredients:
  - 1 [cup] All-purpose flour
  - 1 [cup] Whole wheat flour
  - 1/2 [cup] Sugar
  - 1 [tsp] Baking powder
  - 1 [tsp] Salt
  - 2 Eggs
  - 2 3/4 [cups] Milk
  - 1/4 [cup] Butter, melted

instructions:
  - Mix dry ingredients together in a bowl.
  - In a separate bowl, beat eggs and combine with milk and melted butter.
  - Mix wet ingredients into dry until just combined.
  - Heat a 10 [in] skillet on medium heat until hot.
  - Add a small amount of oil and then 1 [cup] of pancake mixture.
  - Cook for about 1 1/2 [min] on each side or until brown.
```

One thing you should immediately notice is that all units are specified in
square brackets like `[cups]`.  This allows PyCook to know when a quantity is
being used and it will automatically ensure that the unit abbreviations used in
the output are consistently abbreviated and have proper plurals.  It also helps
when it comes to laying out the PDF and recipe cards.

## Cookbook structure

The general structure of a PyCook cookbook is that it's a directory of YAML
files that looks something like this:

```
my_cookbook
├── cookbook.yaml
├── breakfast
│   ├── index.yaml
│   └── cafe-pancakes.yaml
...
```

The `cookbook.yaml` file at the root of the tree is the over-all meta-data file
for your cookbook.  It contains some very basic information like this:

```yaml
# cookbook.yaml
title: Ekstrand Cookbook
author: Jason Ekstrand
```

In each directory that you want to be a cookbook chapter, place an `index.yaml`
file containing information about that chapter:

```yaml
# breakfast/index.yaml
title: Breakfast
```

And that's it!  Throw in some recipes, check it into Git, and you have
a version-controlled cookbook.

## Running PyCook

Assuming you have a project setup as described above, generating the cookbook
is simple.  To get a PDF of your cookbook, run

```sh
pycook.py pdf path/to/cookbook.yaml path/to/output.pdf
```

To get an HTML cookbook, run

```sh
pycook.py html path/to/cookbook.yaml path/to/html/output/dir
```
