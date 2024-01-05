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
            'text-valign': 'center',
            'text-halign': 'center',
            'color': 'white',
            'background-color': '#0074D9'
        },
    },
    {
        'selector': 'node:selected',
        'style': {
            'background-color': '#FF4136'  # Цвет нажатой вершины
        }
    }
]

lattice_stylesheet = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            'text-valign': 'center',
            'text-halign': 'center',
            'color': 'white',
            'background-color': '#0074D9'
        },
    },
    {
        'selector': 'node:selected',
        'style': {
            'background-color': '#FF4136'  # Цвет нажатой вершины
        }
    }
]
