from pyecharts import options as opts
from pyecharts.charts import Graph
from .db import (databaseBursts)

DB_MANAGER = databaseBursts.dbManager()
CLIENT_NAME = databaseBursts.CLIENT_NAME


def generate_full_graph():
    '''
        Generate the overview graph of the smart home
    '''
    # A list of entities
    entities = [e[0] for e in DB_MANAGER.execute('SELECT name FROM entities',None)]
    nodes = []
    for n in entities:
        if n == 'Mocha':
            nodes.append(opts.GraphNode(name='Mocha', x=100, y=300, is_fixed=True))
        elif n == 'Router':
            nodes.append(opts.GraphNode(name='Router', x=100, y=320, is_fixed=True))
        elif n == 'Internet':
            nodes.append(opts.GraphNode(name='Internet', x=100, y=340, is_fixed=True))
        else:
            nodes.append(opts.GraphNode(name=n, x=100, y=100))
    
    # Create an intermediate data structure to collate all links that share the same (source,target) pair, so their protocols can be concatenated
    # Maps (source,target) pair to a set of protocols on that edge
    collected_edges = {}
    all_edges = DB_MANAGER.execute('SELECT source, target, edge_protocol FROM device_data_flow_edges',None)
    for e in all_edges:
        # We made canonical that the smaller name (lexicographically) is source (constraint already coded in database)
        source, target, protocol = e

        if (source,target) in collected_edges:
            collected_edges[(source,target)].add(protocol)
        else:
            collected_edges[(source,target)] = {protocol}
    
    links = []
    for st, ps in collected_edges.items():
        source, target = st
        links.append(opts.GraphLink(source=source, target=target, 
            label_opts=opts.LabelOpts(formatter='/'.join(sorted(ps)), position='middle')))
        
    # Links for Mocha - Router - Internet
    links.append(opts.GraphLink(source='Mocha', target='Router', linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)')))
    links.append(opts.GraphLink(source='Router', target='Internet', linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)')))
        
    c = (
        Graph()
        .add(
            "",
            nodes,
            links,
            is_focusnode=False,
            linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)'),
            edge_length=50,
            repulsion=150,
            symbol_size=20
        )
    )
    
    return c
    
def generate_graph(device, protocol):
    '''
        Generate the graph for selected (`device`, `protocol`)
    '''
    connects_to_internet = DB_MANAGER.execute(
        f'''
            SELECT E.connects_to_internet
            FROM device_data_flow_example E, devices D
            WHERE E.device_id = D.id AND D.name = '{device}' AND E.protocol = '{protocol}'
        '''
    ,None)[0][0]
    entities = [e[0] for e in DB_MANAGER.execute('SELECT name FROM entities',None)]
    edges = set(DB_MANAGER.execute('SELECT source, target FROM device_data_flow_edges',None))
    relevant_edges = {(x[0], x[1]): x[2] for x in DB_MANAGER.execute(
        f'''
            SELECT source, target, edge_protocol
            FROM device_data_flow_edges E, devices D
            WHERE E.device_id = D.id AND D.name = '{device}' AND E.protocol = '{protocol}'
        '''
    ,None)}  # A dictionary mapping (source,target) to the protocol that runs on that edge
    relevant_nodes = {e[0] for e in relevant_edges.keys()} | {e[1] for e in relevant_edges.keys()}

    nodes = []
    for n in entities:
        if n == 'Mocha':
            nodes.append(opts.GraphNode(name='Mocha', x=100, y=300, is_fixed=True))
        elif n == 'Router':
            nodes.append(opts.GraphNode(name='Router', x=100, y=320, is_fixed=True))
        elif n == 'Internet':
            nodes.append(opts.GraphNode(name='Internet', x=100, y=340, is_fixed=True))
        else:
            if n in relevant_nodes:
                nodes.append(opts.GraphNode(name=n, x=100, y=100))
            else:
                nodes.append(opts.GraphNode(name=n, x=100, y=100, category=0))

    links = [] 
    for e in edges:
        if e in relevant_edges:
            links.append(opts.GraphLink(source=e[0], target=e[1], 
                linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)'),
                label_opts=opts.LabelOpts(formatter=relevant_edges[e], position='middle')))
        else:
            links.append(opts.GraphLink(source=e[0], target=e[1], 
                linestyle_opts=opts.LineStyleOpts(color='rgb(178,190,181)')))

    links.append(opts.GraphLink(source='Mocha', target='Router', 
        linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)' if connects_to_internet else 'rgb(178,190,181)')))
    links.append(opts.GraphLink(source='Router', target='Internet', 
        linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)' if connects_to_internet else 'rgb(178,190,181)')))

    categories = [
        opts.GraphCategory(
            symbol='roundRect',
            symbol_size=5,
            label_opts=opts.LabelOpts(color='rgb(178,190,181)')
        )
    ]
    
    c = (
        Graph()
        .add(
            "",
            nodes,
            links,
            categories,
            is_focusnode=False,
            edge_length=50,
            repulsion=150,
            symbol_size=20
        )
    )
    
    return c

