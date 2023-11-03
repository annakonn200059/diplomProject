default_stylesheet = [
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",  # Добавьте это для кривых стрелок
            "target-arrow-shape": "triangle",  # Это делает рёбра ориентированными
        },
    },
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
        },
    },
]
