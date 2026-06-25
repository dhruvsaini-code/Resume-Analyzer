import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Tuple

# Simple list of English stopwords for keyword frequency counting
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", 'using', 'used', 'use', 'also',
    'work', 'experience', 'key', 'project', 'led', 'built', 'developed'
}

class ResumeCharts:
    """
    Class holding helper methods to construct visual widgets and charts.
    """
    
    @staticmethod
    def create_gauge_chart(value: float, title: str, color: str = "#0D9488") -> go.Figure:
        """
        Creates a clean Gauge chart for scores.
        """
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 16, 'color': '#D1D5DB'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': '#9CA3AF'},
                'bar': {'color': color},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 1,
                'bordercolor': '#4B5563',
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.1)'},
                    {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.1)'},
                    {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                ]
            }
        ))
        fig.update_layout(
            height=200, 
            margin=dict(l=30, r=30, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_radar_chart(scores_dict: Dict[str, float]) -> go.Figure:
        """
        Creates a Radar chart showing the breakdown of composite scores.
        """
        categories = list(scores_dict.keys())
        values = list(scores_dict.values())
        
        # Close the shape
        categories = categories + [categories[0]]
        values = values + [values[0]]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line_color='#6366F1',
            fillcolor='rgba(99, 102, 241, 0.25)',
            marker=dict(color='#818CF8', size=6)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    color='#9CA3AF',
                    gridcolor='#374151'
                ),
                angularaxis=dict(
                    color='#F3F4F6',
                    gridcolor='#374151'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            height=320,
            margin=dict(l=50, r=50, t=30, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def create_sunburst_chart(skills_by_cat: Dict[str, List[str]]) -> go.Figure:
        """
        Generates a hierarchical sunburst chart of extracted skills.
        """
        ids = ["Skills"]
        labels = ["Skills Inventory"]
        parents = [""]
        values = [0]
        
        total_skills = 0
        for cat, skills in skills_by_cat.items():
            if not skills:
                continue
            cat_label = cat.replace('_', ' ').title()
            ids.append(f"Skills/{cat}")
            labels.append(cat_label)
            parents.append("Skills")
            values.append(len(skills))
            total_skills += len(skills)
            
            for sk in skills:
                ids.append(f"Skills/{cat}/{sk}")
                labels.append(sk)
                parents.append(f"Skills/{cat}")
                values.append(1)
                
        values[0] = total_skills
        
        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=px.colors.qualitative.Pastel),
            hovertemplate='<b>%{label}</b><br>Count: %{value}'
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_treemap_chart(skills_by_cat: Dict[str, List[str]]) -> go.Figure:
        """
        Generates a treemap representation of skills.
        """
        ids = []
        labels = []
        parents = []
        values = []
        
        for cat, skills in skills_by_cat.items():
            if not skills:
                continue
            cat_label = cat.replace('_', ' ').title()
            ids.append(cat)
            labels.append(cat_label)
            parents.append("")
            values.append(len(skills))
            
            for sk in skills:
                ids.append(f"{cat}_{sk}")
                labels.append(sk)
                parents.append(cat)
                values.append(1)
                
        fig = go.Figure(go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colorscale='tealgrn'),
            textinfo="label+value"
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_skill_distribution_chart(skills_by_cat: Dict[str, List[str]]) -> go.Figure:
        """
        Simple bar plot of skill counts per category.
        """
        data = []
        for cat, skills in skills_by_cat.items():
            data.append({
                'Category': cat.replace('_', ' ').title(),
                'Skills Count': len(skills)
            })
        df = pd.DataFrame(data)
        
        fig = px.bar(
            df,
            x='Skills Count',
            y='Category',
            orientation='h',
            color='Skills Count',
            color_continuous_scale='blues',
            template='plotly_dark'
        )
        fig.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_experience_timeline(timeline_list: List[Dict[str, Any]]) -> go.Figure:
        """
        Builds a horizontal Gantt timeline of the candidate's career.
        """
        if not timeline_list:
            return go.Figure()
            
        df = pd.DataFrame(timeline_list)
        df = df.sort_values(by='start_year', ascending=True).reset_index(drop=True)
        
        fig = go.Figure()
        
        for i, row in df.iterrows():
            duration = row['duration_years']
            fig.add_trace(go.Bar(
                name=f"{row['role']} @ {row['company']}",
                y=[f"{row['role']}<br><sub>{row['company']}</sub>"],
                x=[duration],
                base=[row['start_year']],
                orientation='h',
                marker=dict(
                    color=px.colors.sequential.Teal[i % len(px.colors.sequential.Teal)],
                    line=dict(color='#1E293B', width=1)
                ),
                text=f"{row['start_year']} - {row['end_year_label']}",
                textposition='inside',
                insidetextanchor='middle',
                hoverinfo='name'
            ))
            
        fig.update_layout(
            barmode='stack',
            showlegend=False,
            height=max(180, len(df) * 60),
            margin=dict(l=150, r=30, t=40, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'},
            xaxis=dict(
                type='linear',
                title="Years",
                tickmode='linear',
                dtick=1,
                gridcolor='#374151',
                color='#9CA3AF'
            ),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0)',
                color='#F3F4F6'
            )
        )
        return fig

    @staticmethod
    def create_donut_chart(values: List[float], labels: List[str], title: str) -> go.Figure:
        """
        Standard styled donut chart.
        """
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.5,
            marker=dict(colors=px.colors.qualitative.Safe),
            hoverinfo='label+percent'
        )])
        fig.update_layout(
            title={'text': title, 'font': {'size': 16, 'color': '#F3F4F6'}},
            showlegend=True,
            legend=dict(font=dict(color='#D1D5DB')),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_keyword_frequency_chart(text: str) -> go.Figure:
        """
        Visualizes the top 15 terms found in the resume.
        """
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [w for w in words if w not in STOPWORDS]
        
        freq = {}
        for w in filtered_words:
            freq[w] = freq.get(w, 0) + 1
            
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:15]
        if not sorted_freq:
            return go.Figure()
            
        df = pd.DataFrame(sorted_freq, columns=['Keyword', 'Frequency'])
        
        fig = px.bar(
            df,
            x='Frequency',
            y='Keyword',
            orientation='h',
            color='Frequency',
            color_continuous_scale='purples',
            template='plotly_dark'
        )
        fig.update_layout(
            height=380,
            margin=dict(l=100, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_heatmap_chart(skills_by_cat: Dict[str, List[str]]) -> go.Figure:
        """
        Draws a density correlation representation showing categories vs skills presence.
        """
        categories = [cat.replace('_', ' ').title() for cat in skills_by_cat.keys()]
        counts = [len(skills) for skills in skills_by_cat.values()]
        
        # Turn into a simple 2D matrix
        z_data = np.array(counts).reshape(1, -1)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=categories,
            y=["Skills Density"],
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            height=180,
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'},
            yaxis=dict(showgrid=False, tickmode='array', tickvals=[0], ticktext=["Density"])
        )
        return fig

    @staticmethod
    def create_skill_category_comparison(resume_skills: Dict[str, List[str]], jd_skills: Dict[str, List[str]]) -> go.Figure:
        """
        Plots a side-by-side grouped bar chart of Candidate vs Job Post requirements.
        """
        categories = list(resume_skills.keys())
        
        cand_counts = [len(resume_skills[cat]) for cat in categories]
        jd_counts = [len(jd_skills[cat]) for cat in categories]
        
        clean_cats = [cat.replace('_', ' ').title() for cat in categories]
        
        fig = go.Figure(data=[
            go.Bar(name='Candidate Profile', x=clean_cats, y=cand_counts, marker_color='#0D9488'),
            go.Bar(name='Job Requirements', x=clean_cats, y=jd_counts, marker_color='#E11D48')
        ])
        
        fig.update_layout(
            barmode='group',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'},
            xaxis=dict(gridcolor='#374151', color='#9CA3AF'),
            yaxis=dict(gridcolor='#374151', color='#9CA3AF', title="Number of Skills")
        )
        return fig

    @staticmethod
    def create_section_completeness_chart(section_status: Dict[str, bool]) -> go.Figure:
        """
        Donut chart tracking section quality checks.
        """
        found = sum(1 for v in section_status.values() if v)
        missing = len(section_status) - found
        
        fig = go.Figure(data=[go.Pie(
            labels=['Present', 'Missing'],
            values=[found, missing],
            hole=.6,
            marker=dict(colors=['#10B981', '#EF4444']),
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            showlegend=False,
            height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'}
        )
        return fig

    @staticmethod
    def create_role_probability_graph(probs: List[Tuple[str, float]]) -> go.Figure:
        """
        Horizontal bar showing ML probability predictions.
        """
        df = pd.DataFrame(probs, columns=["Career Role", "Probability Confidence (%)"])
        df = df.sort_values(by="Probability Confidence (%)", ascending=True)
        
        fig = px.bar(
            df,
            x="Probability Confidence (%)",
            y="Career Role",
            orientation="h",
            color="Probability Confidence (%)",
            color_continuous_scale="blues",
            template='plotly_dark'
        )
        fig.update_layout(
            height=250, 
            margin=dict(l=130, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F3F4F6'},
            coloraxis_showscale=False
        )
        return fig
