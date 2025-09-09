import networkx as nx
from collections import Counter
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
import random 
import textalloc as ta
import plotly.graph_objs as go



def CreateNetworkFromRandomClasses(n_of_class_nodes, n_edges):
    Net=nx.Graph()
    net_data=list(zip([f'Class{i}' for i in range(len(n_of_class_nodes))],[n for n in n_of_class_nodes]))
    i=0
    for d in net_data:
        for step in range(d[1]):
            Net.add_node(i,Type=d[0],Name='node_'+str(i))
            i+=1
    nod=list(Net.nodes())
    edges=[random.sample(nod,2) for _ in range(n_edges)]


    Net.add_edges_from(edges)
    
    return Net




def visualize_network(G,layout='auto',figure_size=(15,10),figure_title='',mode='2d',
                      node_color_attribute=False,node_annotation = False, node_shape = 'o', node_size=100, node_alpha=1,node_outline='black', show_node_label_3d = False,
                      edge_attribute_width = False,factor_edge_width = 1 ,cmap = "viridis" ,edge_color_attribute=False, edge_annotation_attributes = False 
                      ,edge_linewidth=0.5,edge_alpha=0.5,edge_color='black',
                      annotation_arrows = False, text_size = 10, text_color = 'black', text_margin = 0.01, 
                      text_min_distance = 0.015, text_max_distance = 0.07,dpi = 300, 
                      plot_cbar=False, cbar_title = '', cbar_ticks_fontsize = 10, cbar_shrink = 1.0, cbar_aspect = 20, 
                      cbar_pad = 0.05,cbar_orientation = 'vertical',cbar_location = 'right', cbar_label_fontsize = 20,
                      save=False,legend=False):
    
# ===========================================================================================================================


#                                              GATHER DATA FROM THE NETWORK


#============================================================================================================================
        

    
#          =============================================== EDGES ===================================================

    # COLOR        
    if edge_color_attribute:
        edge_colors = []
        for (source,target,attributedict) in G.edges(data = True):
            try:
                edge_colors.append(attributedict[edge_color_attribute])
            except:
                edge_colors.append('black')
    else:
        edge_colors = ['black' for edge in G.edges]




    # TICKNESS        
    if edge_attribute_width:
        edge_widths = []
        for (source,target,attributedict) in G.edges(data = True):
            try:
                edge_widths.append(factor_edge_width * np.abs(attributedict[edge_attribute_width]))
            except:
                edge_widths.append(np.abs(edge_linewidth))
    else:
        edge_widths = [np.abs(edge_linewidth) for edge in G.edges]
                
    # ANNOTATION        
    if edge_annotation_attributes:
        edge_annotations = []
        for (source,target,attributedict) in G.edges(data = True):
            anno_dict = {}
            if len(set(edge_annotation_attributes).intersection(set(list(attributedict.keys())))) >= 1: # Check if there is at least one interesting thing to annotate
                for ann in edge_annotation_attributes:
                    try:                    
                        anno_dict[ann] = attributedict[ann]
                    except:
                        pass
                
                edge_annotations.append(str(anno_dict))   
            
            else:
                edge_annotations.append('')
    else:
        edge_annotations = ['' for edge in G.edges]


#           =============================================== NODES ===================================================

    
    if node_color_attribute:
        NodeClasses = []
        for n in G.nodes(data = True):
            try:
                NodeClasses.append(n[1][node_color_attribute])
            except:
                NodeClasses.append('unknown')
        
        if all([isinstance(classe,str) for classe in NodeClasses]):
            # Here we will detect automatically if we need to use a categorical color type or continuous one
        
            N = len(set(NodeClasses))
            Cdict=dict(zip(set(NodeClasses),[n for n in range(N)]))
            NodeColors = list(map(Cdict.get,NodeClasses))

            colors  = [f"C{i}" for i in np.arange(1, max(NodeColors)+1)]
    #             cmap, norm = matplotlib.colors.from_levels_and_colors(np.arange(1, max(NodeColors)+2), colors)
        else:
            
            NodeColors = NodeClasses

    else:
        N = len(G.nodes)
        NodeColors = [0 for n in range(N)]
        colors  = [f"C{i}" for i in np.arange(1, max(NodeColors)+1)]
#             cmap, norm = None,None



# ===========================================================================================================================

#          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 2D MODE  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#============================================================================================================================
     
    
    
    
    
    if mode=='2d':
        
#           =============================================== NODES ===================================================

        
        if layout == 'auto':
            iG=ig.Graph.from_networkx(G)
            my_layout=iG.layout_auto()
            node_coordinates=dict(zip([v['_nx_name'] for v in list(iG.vs)],my_layout.coords))
        elif layout == 'spring':
            node_coordinates=nx.spring_layout(G)
        elif layout == 'circular':
            node_coordinates=nx.circular_layout(G)
        elif layout== 'spectral':
            node_coordinates=nx.spectral_layout(G)
        elif layout == 'hierarchical':
            node_coordinates = nx.drawing.nx_agraph.graphviz_layout(G, prog = 'dot')
        elif layout == 'kk':
            node_coordinates=nx.kamada_kawai_layout(G)

            

        
        sources = [s[0] for s in G.edges()]
        targets = [s[1] for s in G.edges()]
        
        edges_coordinates=[]
        for edge in list(zip(sources,targets)):
            edges_coordinates.append(list(map(node_coordinates.get,edge)))


#          ==================================================BUILD THE FIGURE ==================================================
        fig,ax=plt.subplots(figsize=figure_size) 
        
        

        
        
        
        
        #PLOT
        for i,point in enumerate(edges_coordinates):
            ax.plot((point[0][0],point[1][0]),(point[0][1],point[1][1]),
                    color=edge_colors[i],
                    linewidth=edge_widths[i],
                    alpha=edge_alpha,
                    zorder=0)

        
        
        
        xses=[x[0] for x in node_coordinates.values()]
        yses=[y[1] for y in node_coordinates.values()]
        
        
        
        
        scatter=ax.scatter(xses,
                yses, 
                alpha=node_alpha ,
                edgecolors=node_outline,
                marker = node_shape,
                c=NodeColors,
                zorder=1,
                s=node_size,
                cmap=cmap)
        lab=[]
        if node_annotation:
            
            lab=[n[1][node_annotation] for n in G.nodes]
            ta.allocate_text(fig,
                            ax,
                            xses,
                            yses,
                            lab,
                            draw_lines=annotation_arrows,
                            textsize = text_size,
                            textcolor = text_color,
                            margin = text_margin,
                            min_distance = text_min_distance,
                            max_distance = text_max_distance
                            )
        if legend:
            
            lab = []
            for n in G.nodes(data = True):
                try:
                    lab.append(n[1][legend])
                except:
                    lab.append('unknown')
            handles,labels=scatter.legend_elements()[0],set(lab)
            ax.legend(handles=handles,labels=labels, loc="best")
            
        
        
        
        ax.axis('off')
        if plot_cbar:
            cbar = plt.colorbar(scatter,ax=ax,
                         shrink = cbar_shrink, location = cbar_location, orientation = cbar_orientation,
                         aspect = cbar_aspect, pad = cbar_pad )
            cbar.ax.tick_params(labelsize = cbar_ticks_fontsize)
            cbar.ax.set_ylabel(cbar_title,fontsize = cbar_label_fontsize)
        plt.tight_layout()
        if save:
            plt.savefig(save,dpi=dpi)

        plt.show()

# ===========================================================================================================================

#          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 3D MODE  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#============================================================================================================================
    
    
    elif mode=='3d':
        
        #LAYOUTS ========================================================================================================================
        if layout=='auto':
            iG=ig.Graph.from_networkx(G)
            my_layout=iG.layout_auto(dim=3)
            node_coordinates=dict(zip([v['_nx_name'] for v in list(iG.vs)],my_layout.coords))
        
        if layout == 'kk':
            node_coordinates=nx.kamada_kawai_layout(G,dim=3)
        elif layout == 'spring':
            node_coordinates=nx.spring_layout(G,dim=3)
        elif layout== 'spectral':
            node_coordinates=nx.spectral_layout(G,dim=3)
        
        
        #==================================================DEFINE XYZ OF THE SCATTERS AND EDGES========================================
        
        Xn=[coords[0] for coords in node_coordinates.values()]# x-coordinates of nodes
        Yn=[coords[1] for coords in node_coordinates.values()]# y-coordinates
        Zn=[coords[2] for coords in node_coordinates.values()]# z-coordinates
        
        Xe=sum([(node_coordinates[e[0]][0], node_coordinates[e[1]][0],None) for e in G.edges()],())# x-coordinates of edge ends
        Ye=sum([(node_coordinates[e[0]][1], node_coordinates[e[1]][1],None) for e in G.edges()],())
        Ze=sum([(node_coordinates[e[0]][2], node_coordinates[e[1]][2],None) for e in G.edges()],())
    
        traces = []
     
            
        #==================================================    LABELS    ============================================

        if node_annotation:
            lab=[n[1][node_annotation] for n in G.nodes]
            labdict = dict(zip(list(G.nodes()),lab))
        else:
            lab = []
            labdict = dict(zip(list(G.nodes),['' for n in G.nodes]))        
        
        
        #==================================================     NODE COLORS    ========================================

        if node_color_attribute:
            NodeClasses = []
            for n in G.nodes(data=True):
                try:
                    NodeClasses.append(n[1][node_color_attribute])
                except:
                    NodeClasses.append('unknown')
                
            N = len(set(NodeClasses))
            Cdict=dict(zip(set(NodeClasses),[n for n in range(N)]))
            NodeColors = list(map(Cdict.get,NodeClasses))
            
            
            class_color_dict = dict(zip(NodeClasses,NodeColors))
            
        #==================================================     EDGE COLORS    ========================================
            
            n = 0
            t = 2
            for i in range(len(Xe)//3):
                edge_trace = go.Scatter3d(x=Xe[n:t], y=Ye[n:t], z=Ze[n:t],
                   mode='lines',
                   line=dict(color=edge_colors[i], width=factor_edge_width * edge_widths[i]),
                   hoverinfo='text',
                   hovertext = edge_annotations[i],
                   showlegend=False
                   )
                n += 3
                t += 3
                traces.append(edge_trace)
                
            nodes_unknown = [n[0] for n in G.nodes(data = True) if n[1] == {}]
            nodes_known = [n for n in G.nodes(data = True) if n[1] != {}]
            for Class in set(NodeClasses):
                if Class == 'unknown':
                    ClassNodes = nodes_unknown
                else:
                    ClassNodes = [n[0] for n in nodes_known if n[1][node_color_attribute] == Class]


                        
                    
                ClassLabels = [labdict[n] for n in ClassNodes]
                Xc = [node_coordinates[n][0] for n in ClassNodes]
                Yc = [node_coordinates[n][1] for n in ClassNodes]
                Zc = [node_coordinates[n][2] for n in ClassNodes]

                nodes_trace = go.Scatter3d(x=Xc,
                            y=Yc,
                            z=Zc,
                            mode='markers',
                            name=Class,
                            marker=dict(symbol='circle',
                                            size=node_size/10,
                                            color=class_color_dict[Class],
                                            colorscale=cmap,
                                            line=dict(color='rgb(50,50,50)', width=0.5)
                                            ),
                            hovertext=ClassLabels,
                            hoverinfo='text',
                            showlegend = True
                            )
         #==================================================  ADD VISIBLE LABELS   ========================================
 
                if show_node_label_3d:
                    nodes_trace.update({'text':ClassLabels})
                    nodes_trace.update({'hoverinfo':'none'})
                    nodes_trace.update({'mode':'text'})
                
                traces.append(nodes_trace)

            

        else:
        #==================================================  NO NODE COLORS   ========================================
              
            
            
            NodeColors = [0 for n in range(N)]
            colors  = [f"C{i}" for i in np.arange(1, max(NodeColors)+1)]
        
        
        
            traces = []
        
        

            n = 0
            t = 2
            for i in range(len(Xe)//3):
                trace = go.Scatter3d(x=Xe[n:t], y=Ye[n:t], z=Ze[n:t],
                   mode='lines',
                   line=dict(color=edge_colors[i], width=factor_edge_width * edge_widths[i]),
                   hoverinfo='text',
                   hovertext = edge_annotations[i],
                   showlegend=False
                   )
                n += 3
                t += 3
                traces.append(trace)

            nodes_trace = go.Scatter3d(x=Xn,
                            y=Yn,
                            z=Zn,
                            mode='markers',
                            name='Nodes',
                            marker=dict(symbol='circle',
                                            size=node_size/10,
                                            line=dict(color='rgb(50,50,50)', width=0.5)
                                            ),
                            hovertext=lab,
                            hoverinfo='text',
                            showlegend = False
                            )
            
         #==================================================  ADD VISIBLE LABELS   ========================================
       
            node_counter=0
            if show_node_label_3d:
                nodes_trace.update({'text':lab})
                nodes_trace.update({'hoverinfo':'none'})
                nodes_trace.update({'mode':'text'})
            
            traces.append(nodes_trace)

                    
        #==================================================  FIX LAYOUT OF THE FIG   ========================================

        axis=dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

        fig_layout = go.Layout(
                title=figure_title,
                width=1000,
                height=1000,
                showlegend=True,
                scene=dict(
                    xaxis=dict(axis),
                    yaxis=dict(axis),
                    zaxis=dict(axis),
                ))
        data=traces
        fig=go.Figure(data=data, 
                      layout=fig_layout
                      )
        
        fig.show()
        if save:
            fig.write_html(save)
    
    elif mode == 'cytoscape':
        
        pass # STILL TO BE IMPLEMENTED

















def plot_degree_distribution(graph,save_fig=False,dpi = 300):
    degree=[val for (node, val) in graph.degree()]
    freqdict=Counter(degree)
    frequency=[]
    frequency0=[]
    degree0=[]
    for x in degree:
        if x==0:
            degree0.append(0)
            frequency0.append(freqdict[x])
        else:
            frequency.append(freqdict[x])

    fig, ax= plt.subplots(figsize=(20,10))
    datax=np.log10([elem for elem in degree if elem!=0])
    datay=np.log10(frequency)

    #PLOT DEGREE == 0  NODES  IF THERE ARE ANY
    if len(frequency0)>0:
        ax.scatter(datax,datay, alpha=0.5,s=300,edgecolor='b')
        ax.scatter(-0.1,np.log10(freqdict[0]),alpha=0.5,s=300,edgecolor='red')
    else:
        ax.scatter(datax,datay, alpha=0.5,s=300,edgecolor='b')

    ##CHOOSE THE DEGREES TICKS TO DISPLAY                    
    ax.set_yticks(np.log10(np.geomspace(1,max(frequency),20,dtype=int)))
    ax.set_yticklabels(np.geomspace(1,max(frequency),20,dtype=int),fontsize=12)


    ##CHOOSE THE DEGREES TICKS TO DISPLAY
    ax.set_xticks(np.log10(np.geomspace(1,max(degree),20,dtype=int)))
    ax.set_xticklabels(np.geomspace(1,max(degree),20,dtype=int),fontsize=12)


    ax.grid()
    ax.set_xlabel('Degree',fontsize=20)
    ax.set_ylabel('Frequency',fontsize=20)
    ax.set_xlim(-0.150)
    
    
    if save_fig:
        plt.savefig(save_fig,dpi=dpi)
    plt.show()