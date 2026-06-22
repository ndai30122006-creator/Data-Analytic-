"""Molecular Structure Visualization - Animated Particle Orbit System"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import random
random.seed(42)

def build_molecule(df, filename):
    """Build interactive 3D molecular structure with orbiting particles + trails"""
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object","str","category"]).columns.tolist()
    
    n_particles = min(len(num_cols) if num_cols else 5, 18)
    if n_particles == 0:
        n_particles = min(len(cat_cols) if cat_cols else 4, 14)
    
    fig = go.Figure()
    
    # ── Molecular Nucleus ──────────────────────────────────
    t = np.linspace(0, 2 * np.pi, 40)
    p = np.linspace(0, np.pi, 40)
    
    # Central core
    x_core = 1.2 * np.outer(np.cos(t), np.sin(p))
    y_core = 1.2 * np.outer(np.sin(t), np.sin(p))
    z_core = 1.2 * np.outer(np.ones(40), np.cos(p))
    
    fig.add_trace(go.Surface(
        x=x_core, y=y_core, z=z_core,
        colorscale=[[0, '#f0e6d3'], [0.5, '#c08457'], [1, '#8b5e34']],
        showscale=False, opacity=0.95,
        name="Nucleus",
        hovertemplate="<b>Data Molecule</b><br>Core Nucleus<extra></extra>"
    ))
    
    # Core glow
    x_glow = 1.8 * np.outer(np.cos(t), np.sin(p))
    y_glow = 1.8 * np.outer(np.sin(t), np.sin(p))
    z_glow = 1.8 * np.outer(np.ones(40), np.cos(p))
    
    fig.add_trace(go.Surface(
        x=x_glow, y=y_glow, z=z_glow,
        colorscale=[[0, 'rgba(192,132,87,0.15)'], [1, 'rgba(139,94,52,0)']],
        showscale=False, opacity=0.3,
        name="Aura", showlegend=False
    ))
    
    # Core energy ring
    ring_t = np.linspace(0, 2 * np.pi, 60)
    for ring_r, ring_op in [(2.5, 0.06), (3.0, 0.04)]:
        rx = ring_r * np.cos(ring_t)
        ry = ring_r * np.sin(ring_t)
        rz = np.zeros_like(ring_t)
        fig.add_trace(go.Scatter3d(
            x=rx, y=ry, z=rz,
            mode='lines',
            line=dict(color=f'rgba(108,92,231,{ring_op})', width=1),
            showlegend=False, hoverinfo='skip'
        ))
    
    # ── Inner atoms ──────────────────────────────────────
    nuc_angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)
    colors_inner = ['#6c5ce7', '#00cec9', '#fd79a8', '#e17055', '#00b894', '#fdcb6e']
    
    for i, angle in enumerate(nuc_angles):
        x_n = 2.5 * math.cos(angle)
        y_n = 2.5 * math.sin(angle)
        z_n = 0.8 * math.cos(angle * 2)
        
        fig.add_trace(go.Scatter3d(
            x=[0, x_n], y=[0, y_n], z=[0, z_n],
            mode='lines',
            line=dict(color='rgba(192,132,87,0.25)', width=2),
            showlegend=False, hoverinfo='skip'
        ))
        
        r_atom = 0.5
        t2 = np.linspace(0, 2 * np.pi, 12)
        p2 = np.linspace(0, np.pi, 12)
        x_atom = x_n + r_atom * np.outer(np.cos(t2), np.sin(p2))
        y_atom = y_n + r_atom * np.outer(np.sin(t2), np.sin(p2))
        z_atom = z_n + r_atom * np.outer(np.ones(12), np.cos(p2))
        
        fig.add_trace(go.Surface(
            x=x_atom, y=y_atom, z=z_atom,
            colorscale=[[0, colors_inner[i]], [0.6, colors_inner[i]], [1, 'rgba(255,255,255,0.2)']],
            showscale=False, opacity=0.8,
            name=f"Inner {i+1}",
            hovertemplate=f"<b>Inner Atom {i+1}</b><extra></extra>"
        ))
    
    # ── Orbital Shells ────────────────────────────────────
    colors = ['#818cf8', '#34d399', '#fbbf24', '#f87171', '#38bdf8', 
              '#a78bfa', '#fb923c', '#2dd4bf', '#f472b6', '#4ade80',
              '#e879f9', '#22d3ee', '#fdba74', '#86efac', '#c4b5fd',
              '#67e8f9', '#fda4af', '#d8b4fe', '#6ee7b7', '#fde047']
    
    if num_cols:
        particle_names = num_cols[:n_particles]
    else:
        particle_names = cat_cols[:n_particles]
    
    if n_particles <= 6:
        n_shells, parts = 1, [n_particles]
    elif n_particles <= 12:
        n_shells, parts = 2, [n_particles - n_particles//2, n_particles//2]
        parts.sort(reverse=True)
    else:
        a = min(7, n_particles - 8)
        b = min(8, n_particles - a)
        c = n_particles - a - b
        n_shells, parts = 3, [a, b, c]
        parts = [x for x in parts if x > 0]
        n_shells = len(parts)
    
    shell_radii = [6, 9, 12]
    particle_data_list = []
    
    particle_idx = 0
    for shell in range(n_shells):
        n_in_shell = min(parts[shell], n_particles - particle_idx)
        if n_in_shell <= 0:
            continue
        
        r_shell = shell_radii[shell]
        tilt_x = 0.15 * (shell + 1)
        tilt_y = 0.12 * (shell + 1)
        
        theta_ring = np.linspace(0, 2 * np.pi, 60)
        x_ring = r_shell * np.cos(theta_ring)
        y_ring = r_shell * np.sin(theta_ring) * 0.85
        z_ring = r_shell * np.sin(theta_ring * 2) * 0.15
        
        ax, az = tilt_x * shell, tilt_y * (shell + 1)
        for pt in range(len(x_ring)):
            rx, ry, rz = x_ring[pt], y_ring[pt], z_ring[pt]
            ry2 = ry * math.cos(ax) - rz * math.sin(ax)
            rz2 = ry * math.sin(ax) + rz * math.cos(ax)
            rx3 = rx * math.cos(az) - ry2 * math.sin(az)
            ry3 = rx * math.sin(az) + ry2 * math.cos(az)
            x_ring[pt], y_ring[pt], z_ring[pt] = rx3, ry3, rz2
        
        fig.add_trace(go.Scatter3d(
            x=x_ring, y=y_ring, z=z_ring,
            mode='lines',
            line=dict(color=f'rgba(108, 92, 231, {0.08 + shell * 0.03})', width=1.2),
            showlegend=False, hoverinfo='skip'
        ))
        
        angles = np.linspace(0, 2 * np.pi, n_in_shell, endpoint=False)
        random.shuffle(angles)
        
        for j, theta0 in enumerate(angles):
            if particle_idx >= len(particle_names):
                break
            
            name = particle_names[particle_idx]
            color = colors[particle_idx % len(colors)]
            speed = 0.5 + random.random() * 1.0
            
            if name in num_cols:
                cv = df[name].std() / max(abs(df[name].mean()), 0.01)
                size = min(max(2 + cv * 2.5, 1.5), 6)
            else:
                size = 2.8
            
            if name in num_cols:
                stats_text = (f"<b>{name}</b><br>"
                             f"Mean: {df[name].mean():,.2f}<br>"
                             f"Std: {df[name].std():,.2f}<br>"
                             f"Shell {shell+1}")
            else:
                top_val = df[name].value_counts().index[0]
                stats_text = (f"<b>{name}</b><br>"
                             f"Unique: {df[name].nunique()}<br>"
                             f"Top: {top_val}<br>"
                             f"Shell {shell+1}")
            
            def pos_at_angle(theta):
                px = r_shell * math.cos(theta)
                py = r_shell * math.sin(theta) * 0.85
                pz = r_shell * math.sin(theta * 2) * 0.15
                aax = tilt_x * shell
                aaz = tilt_y * (shell + 1)
                py2 = py * math.cos(aax) - pz * math.sin(aax)
                pz2 = py * math.sin(aax) + pz * math.cos(aax)
                px3 = px * math.cos(aaz) - py2 * math.sin(aaz)
                py3 = px * math.sin(aaz) + py2 * math.cos(aaz)
                return px3, py3, pz2
            
            px, py, pz = pos_at_angle(theta0)
            s = size * 0.3
            
            particle_data_list.append(dict(
                name=name, shell=shell, radius=r_shell,
                angle=theta0, size=size, color=color,
                x=px, y=py, z=pz, speed=speed,
                tilt_x=tilt_x, tilt_y=tilt_y
            ))
            
            # Trail dots
            n_trail = 8
            for ti in range(1, n_trail + 1):
                trail_angle = theta0 - ti * 0.12 * speed
                tx, ty, tz = pos_at_angle(trail_angle)
                trail_opacity = 0.25 * (1 - ti / (n_trail + 1))
                trail_size = max(0.3, s * (1 - ti / (n_trail + 1)) * 0.6)
                trail_color = f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},{trail_opacity})'
                
                fig.add_trace(go.Scatter3d(
                    x=[tx], y=[ty], z=[tz],
                    mode='markers',
                    marker=dict(size=trail_size, color=trail_color, symbol='circle'),
                    showlegend=False, hoverinfo='skip'
                ))
            
            # Main particle
            u = np.linspace(0, 2 * np.pi, 12)
            v = np.linspace(0, np.pi, 12)
            x_sphere = px + s * np.outer(np.cos(u), np.sin(v))
            y_sphere = py + s * np.outer(np.sin(u), np.sin(v))
            z_sphere = pz + s * np.outer(np.ones(12), np.cos(v))
            
            fig.add_trace(go.Surface(
                x=x_sphere, y=y_sphere, z=z_sphere,
                colorscale=[[0, color], [0.5, color], [1, 'rgba(255,255,255,0.3)']],
                showscale=False, opacity=0.9,
                name=name,
                hovertemplate=stats_text + "<extra></extra>"
            ))
            
            # Glow aura
            s_aura = s * 1.6
            x_aura = px + s_aura * np.outer(np.cos(u), np.sin(v))
            y_aura = py + s_aura * np.outer(np.sin(u), np.sin(v))
            z_aura = pz + s_aura * np.outer(np.ones(12), np.cos(v))
            
            fig.add_trace(go.Surface(
                x=x_aura, y=y_aura, z=z_aura,
                colorscale=[[0, f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)'], 
                           [1, 'rgba(255,255,255,0)']],
                showscale=False, opacity=0.15,
                name=f"{name}_glow", showlegend=False
            ))
            
            # Label
            fig.add_trace(go.Scatter3d(
                x=[px], y=[py], z=[pz + s + 0.4],
                mode='text',
                text=[name[:10] + ('..' if len(name) > 10 else '')],
                textfont=dict(size=7, color=color),
                showlegend=False, hoverinfo='skip'
            ))
            
            particle_idx += 1
    
    # ── Animation Frames ──────────────────────────────────
    n_frames = 72
    
    def get_pos(r, theta, tx, ty, shell):
        px = r * math.cos(theta)
        py = r * math.sin(theta) * 0.85
        pz = r * math.sin(theta * 2) * 0.15
        ax = tx * shell
        az = ty * (shell + 1)
        py2 = py * math.cos(ax) - pz * math.sin(ax)
        pz2 = py * math.sin(ax) + pz * math.cos(ax)
        px3 = px * math.cos(az) - py2 * math.sin(az)
        py3 = px * math.sin(az) + py2 * math.cos(az)
        return px3, py3, pz2
    
    frames = []
    for fi in range(n_frames):
        fd = []
        prog = fi / n_frames
        
        for pd_ in particle_data_list:
            r = pd_['radius']; tx = pd_['tilt_x']; ty = pd_['tilt_y']
            sh = pd_['shell']; th0 = pd_['angle']; sp = pd_['speed']
            col = pd_['color']; nm = pd_['name']; sz = pd_['size']
            
            angle = th0 + prog * 2 * math.pi * sp
            px, py, pz = get_pos(r, angle, tx, ty, sh)
            s = sz * 0.3
            u = np.linspace(0, 2 * np.pi, 10)
            v = np.linspace(0, np.pi, 10)
            
            for ti in range(1, 7):
                ta = angle - ti * 0.1 * sp
                tx2, ty2, tz2 = get_pos(r, ta, tx, ty, sh)
                top = 0.2 * (1 - ti / 7)
                ts = max(0.2, s * (1 - ti / 7) * 0.5)
                tr = f'rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},{top})'
                fd.append(go.Scatter3d(
                    x=[tx2], y=[ty2], z=[tz2],
                    mode='markers', marker=dict(size=ts, color=tr, symbol='circle'),
                    showlegend=False, hoverinfo='skip'
                ))
            
            x_s = px + s * np.outer(np.cos(u), np.sin(v))
            y_s = py + s * np.outer(np.sin(u), np.sin(v))
            z_s = pz + s * np.outer(np.ones(10), np.cos(v))
            fd.append(go.Surface(
                x=x_s, y=y_s, z=z_s,
                colorscale=[[0, col], [0.5, col], [1, 'rgba(255,255,255,0.3)']],
                showscale=False, opacity=0.9, name=nm,
                hovertemplate=f"<b>{nm}</b><br>Shell {sh+1}<extra></extra>"
            ))
            
            sa = s * 1.5
            x_a = px + sa * np.outer(np.cos(u), np.sin(v))
            y_a = py + sa * np.outer(np.sin(u), np.sin(v))
            z_a = pz + sa * np.outer(np.ones(10), np.cos(v))
            fd.append(go.Surface(
                x=x_a, y=y_a, z=z_a,
                colorscale=[[0, f'rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.06)'], [1, 'rgba(255,255,255,0)']],
                showscale=False, opacity=0.12, name=f"{nm}_g", showlegend=False
            ))
            
            fd.append(go.Scatter3d(
                x=[px], y=[py], z=[pz + s + 0.35],
                mode='text', text=[nm[:10] + ('..' if len(nm) > 10 else '')],
                textfont=dict(size=7, color=col),
                showlegend=False, hoverinfo='skip'
            ))
        
        frames.append(go.Frame(data=fd, name=f"f{fi}"))
    
    # ── Layout ────────────────────────────────────────────
    fig.update_layout(
        title=dict(text=f"<b>Data Molecule</b> &mdash; <i>{filename}</i>",
                   x=0.5, font=dict(size=20, color='#f1f5f9')),
        scene=dict(
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False, range=[-15, 15], autorange=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False, range=[-15, 15], autorange=False),
            zaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False, range=[-13, 13], autorange=False),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=10, y=10, z=8), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
            aspectmode='manual', aspectratio=dict(x=1.15, y=1.15, z=1)
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        margin=dict(l=0, r=0, t=40, b=0), height=800,
        showlegend=False, hovermode='closest',
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.5, y=1.05, xanchor="center",
            buttons=[
                dict(label="Play", method="animate",
                     args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True, mode="immediate", transition=dict(duration=0))]),
                dict(label="Pause", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))]),
                dict(label="Reset View", method="relayout",
                     args=[{"scene.camera": {"eye": {"x": 10, "y": 10, "z": 8}, "center": {"x": 0, "y": 0, "z": 0}, "up": {"x": 0, "y": 0, "z": 1}}}]),
                dict(label="Fast", method="animate",
                     args=[None, dict(frame=dict(duration=20, redraw=True), fromcurrent=True, mode="immediate", transition=dict(duration=0))])
            ]
        )]
    )
    
    fig.frames = frames
    return fig, particle_data_list


def render_solar_system_tab(df, filename):
    st.markdown('<div class="main-header">Data Molecule</div>', unsafe_allow_html=True)
    
    fig, particle_data = build_molecule(df, filename)
    st.plotly_chart(fig, width='stretch')
    
    if particle_data:
        cols = st.columns(min(len(particle_data), 6))
        for i, pd_ in enumerate(particle_data[:6]):
            with cols[i % 6]:
                st.markdown(f"<span style='color:{pd_['color']}'>●</span> {pd_['name']} Ø{pd_['size']:.0f}", unsafe_allow_html=True)
        if len(particle_data) > 6:
            st.caption(f"+ {len(particle_data) - 6} more")
    
    st.caption("Drag to rotate | Scroll to zoom | Hover for stats | Play for orbit animation")