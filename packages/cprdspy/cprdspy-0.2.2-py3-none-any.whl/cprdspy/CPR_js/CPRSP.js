// 绘制一个圆
function circle(center, radius, color = 'blue') {
    const angle = Array.from({ length: 100000 }, (_, i) => (i / 99999) * 2 * Math.PI);
    const x = angle.map(a => center[0] + radius * Math.cos(a));
    const y = angle.map(a => center[1] + radius * Math.sin(a));

    const trace = {
        x: x,
        y: y,
        mode: 'lines',
        line: { color: color }
    };

    const layout = {
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', [trace], layout);
}
// 根据中心点和圆上一点绘制圆
function circle_p(center, point, color = 'blue') {
    const radius = Math.sqrt(Math.pow(point[0] - center[0], 2) + Math.pow(point[1] - center[1], 2));
    const angle = Array.from({ length: 10000 }, (_, i) => (i / 9999) * 2 * Math.PI);
    const x = angle.map(a => center[0] + radius * Math.cos(a));
    const y = angle.map(a => center[1] + radius * Math.sin(a));

    const trace = {
        x: x,
        y: y,
        mode: 'lines',
        line: { color: color }
    };

    const layout = {
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', [trace], layout);
}
// 绘制同心圆（等差，双向）
// function ConcentricCircles(center, n, d, radius, color = 'blue') {
//     const traces = [];

//     // 中心点
//     traces.push({
//         x: [center[0]],
//         y: [center[1]],
//         mode: 'markers',
//         marker: { color: color }
//     });

//     // 绘制同心圆
//     for (let i = 0; i < n; i++) {
//         traces.push(...circle(center, radius - i * d, color).data);
//         traces.push(...circle(center, radius + i * d, color).data);
//     }
//     traces.push(...circle(center, radius, color).data);

//     const layout = {
//         yaxis: { scaleanchor: "x", scaleratio: 1 }
//     };

//     Plotly.newPlot('plot', traces, layout);
// }
// 绘制向外扩展的同心圆
function ConcentricCircles_o(center, n, d, radius, color = 'blue') {
    const traces = [];

    // 中心点
    traces.push({
        x: [center[0]],
        y: [center[1]],
        mode: 'markers',
        marker: { color: color }
    });

    // 绘制向外扩展的圆
    for (let i = 0; i < n; i++) {
        const angle = Array.from({ length: 100000 }, (_, j) => (j / 99999) * 2 * Math.PI);
        const x = angle.map(a => center[0] + (radius + d * i) * Math.cos(a));
        const y = angle.map(a => center[1] + (radius + d * i) * Math.sin(a));

        traces.push({
            x: x,
            y: y,
            mode: 'lines',
            line: { color: color }
        });
    }

    const layout = {
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', traces, layout);
}
// 绘制向内收缩的同心圆
function ConcentricCircles_i(center, n, d, radius, color = 'blue') {
    const traces = [];

    // 中心点
    traces.push({
        x: [center[0]],
        y: [center[1]],
        mode: 'markers',
        marker: { color: color }
    });

    // 绘制向内收缩的圆
    for (let i = 0; i < n; i++) {
        const angle = Array.from({ length: 100000 }, (_, j) => (j / 99999) * 2 * Math.PI);
        const x = angle.map(a => center[0] + (radius - d * i) * Math.cos(a));
        const y = angle.map(a => center[1] + (radius - d * i) * Math.sin(a));

        traces.push({
            x: x,
            y: y,
            mode: 'lines',
            line: { color: color }
        });
    }

    const layout = {
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', traces, layout);
}// 绘制同心圆（等比，双向）
// function ConcentricCircles_Pro(center, n, q, radius, color = 'blue') {
//     const traces = [];

//     // 中心点
//     traces.push({
//         x: [center[0]],
//         y: [center[1]],
//         mode: 'markers',
//         marker: { color: color }
//     });

//     // 绘制同心圆
//     for (let i = 0; i < n; i++) {
//         traces.push(...circle(center, radius / Math.pow(q, i), color).data);
//         traces.push(...circle(center, radius * Math.pow(q, i), color).data);
//     }
//     traces.push(...circle(center, radius, color).data);

//     const layout = {
//         yaxis: { scaleanchor: "x", scaleratio: 1 }
//     };

//     Plotly.newPlot('plot', traces, layout);
// }
// 绘制向外扩展的等比同心圆
function ConcentricCircles_Pro_o(center, n, q, radius, color = 'blue') {
    const traces = [];

    // 中心点
    traces.push({
        x: [center[0]],
        y: [center[1]],
        mode: 'markers',
        marker: { color: color }
    });

    // 绘制向外扩展的等比圆
    for (let i = 0; i < n; i++) {
        const angle = Array.from({ length: 100000 }, (_, j) => (j / 99999) * 2 * Math.PI);
        const x = angle.map(a => center[0] + radius * Math.pow(q, i) * Math.cos(a));
        const y = angle.map(a => center[1] + radius * Math.pow(q, i) * Math.sin(a));

        traces.push({
            x: x,
            y: y,
            mode: 'lines',
            line: { color: color }
        });
    }

    const layout = {
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', traces, layout);
}
// 绘制向内收缩的等比同心圆
function ConcentricCircles_Pro_i(center, n, q, radius, color = 'blue') {
    const traces = [];

    // 中心点
    traces.push({
        x: [center[0]],
        y: [center[1]],
        mode: 'markers',
        marker: { color: color }
    });

    // 绘制向内收缩的等比圆
    for (let i = 0; i < n; i++) {
        const angle = Array.from({ length: 100000 }, (_, j) => (j / 99999) * 2 * Math.PI);
        const x = angle.map(a => center[0] + radius / Math.pow(q, i) * Math.cos(a));
        const y = angle.map(a => center[1] + radius / Math.pow(q, i) * Math.sin(a));

        traces.push({
            x: x,
            y: y,
            mode: 'lines',
            line: { color: color }
        });
    }

    const layout = {
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', traces, layout);
}
// 绘制等差向外扩展的波形圆
function wave_circle_ari_o(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_o([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_o(
            [
                Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 绘制等差向内收缩的波形圆
function wave_circle_ari_i(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_i([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_i(
            [
                Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 绘制等差双向扩展的波形圆
// function wave_circle_ari(A, F, P, color, theta = 0, R = 1) {
//     const fig = [];
//     fig.push(...ConcentricCircles([0, 0], F, A, R, 'green').data);

//     for (let i = 0; i <= P; i++) {
//         const subFig = ConcentricCircles(
//             [
//                 Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
//                 Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
//             ],
//             F,
//             A,
//             R,
//             color
//         );
//         fig.push(...subFig.data);
//     }

//     const layout = {
//         showlegend: false,
//         yaxis: { scaleanchor: "x", scaleratio: 1 }
//     };

//     Plotly.newPlot('plot', fig, layout);
// }
// 绘制等比向外扩展的波形圆
function wave_circle_pro_o(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_Pro_o([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_Pro_o(
            [
                Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 绘制等比向内收缩的波形圆
function wave_circle_pro_i(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_Pro_i([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_Pro_i(
            [
                Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 绘制等比双向扩展的波形圆
function wave_circle_pro(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_Pro([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_Pro(
            [
                Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 绘制等差向外扩展的波形圆（优化）
function wave_circle_ari_o(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_o([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_o(
            [
                R * Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                R * Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 绘制等差向内收缩的波形圆（优化）
function wave_circle_ari_i(A, F, P, color, theta = 0, R = 1) {
    const fig = [];
    fig.push(...ConcentricCircles_i([0, 0], F, A, R, 'green').data);

    for (let i = 0; i <= P; i++) {
        const subFig = ConcentricCircles_i(
            [
                R * Math.cos(i * 2 * Math.PI / P + Math.PI / 2 + theta),
                R * Math.sin(i * 2 * Math.PI / P + Math.PI / 2 + theta)
            ],
            F,
            A,
            R,
            color
        );
        fig.push(...subFig.data);
    }

    const layout = {
        showlegend: false,
        yaxis: { scaleanchor: "x", scaleratio: 1 }
    };

    Plotly.newPlot('plot', fig, layout);
}
// 等差向内波圈
function wave_circle_ari_i(A, F, P, color, theta = 0, R = 1) {
    // 创建初始同心圆
    let fig = ConcentricCircles_i([0, 0], F, A, R, 'g');
    for (let i = 0; i <= P; i++) {
        // 计算每个子圆的位置
        let angle = i * 2 * Math.PI / P + Math.PI / 2 + theta;
        let subFig = ConcentricCircles_i([Math.cos(angle), Math.sin(angle)], F, A, R, color);
        fig.data.push(...subFig.data);
    }
    fig.layout.showlegend = false;
    fig.layout.yaxis = { scaleanchor: "x", scaleratio: 1 };
    return fig;
}

// 等差双向波圈
function wave_circle_ari(A, F, P, color, theta = 0, R = 1) {
    let fig = ConcentricCircles([0, 0], F, A, R, 'g');
    for (let i = 0; i <= P; i++) {
        let angle = i * 2 * Math.PI / P + Math.PI / 2 + theta;
        let subFig = ConcentricCircles([Math.cos(angle), Math.sin(angle)], F, A, R, color);
        fig.data.push(...subFig.data);
    }
    fig.layout.showlegend = false;
    fig.layout.yaxis = { scaleanchor: "x", scaleratio: 1 };
    return fig;
}

// 等比向外波圈
function wave_circle_pro_o(A, F, P, color, theta = 0, R = 1) {
    let fig = ConcentricCircles_Pro_o([0, 0], F, Math.sqrt(A), R, color);
    for (let i = 0; i <= P; i++) {
        let angle = i * 2 * Math.PI / P + Math.PI / 2 + theta;
        let subFig = ConcentricCircles_Pro_o([Math.cos(angle), Math.sin(angle)], F, Math.sqrt(A), R, color);
        fig.data.push(...subFig.data);
    }
    fig.layout.showlegend = false;
    fig.layout.yaxis = { scaleanchor: "x", scaleratio: 1 };
    return fig;
}

// 等比向内波圈
function wave_circle_pro_i(A, F, P, color, theta = 0, R = 1) {
    let fig = ConcentricCircles_Pro_i([0, 0], F, Math.sqrt(A), R, color);
    for (let i = 0; i <= P; i++) {
        let angle = i * 2 * Math.PI / P + Math.PI / 2 + theta;
        let subFig = ConcentricCircles_Pro_i([Math.cos(angle), Math.sin(angle)], F, Math.sqrt(A), R, color);
        fig.data.push(...subFig.data);
    }
    fig.layout.showlegend = false;
    fig.layout.yaxis = { scaleanchor: "x", scaleratio: 1 };
    return fig;
}

// 等比双向波圈
function wave_circle_pro(A, F, P, color, theta = 0, R = 1) {
    let fig = ConcentricCircles_Pro([0, 0], F, Math.sqrt(A), R, color);
    for (let i = 0; i <= P; i++) {
        let angle = i * 2 * Math.PI / P + Math.PI / 2 + theta;
        let subFig = ConcentricCircles_Pro([Math.cos(angle), Math.sin(angle)], F, Math.sqrt(A), R, color);
        fig.data.push(...subFig.data);
    }
    fig.layout.showlegend = false;
    fig.layout.yaxis = { scaleanchor: "x", scaleratio: 1 };
    return fig;
}

// 顺时针弧
function arc(center, point1, point2, color = 'blue') {
    let vector1 = [point1[0] - center[0], point1[1] - center[1]];
    let vector2 = [point2[0] - center[0], point2[1] - center[1]];
    let r1 = Math.sqrt(vector1[0] ** 2 + vector1[1] ** 2);
    let theta1 = Math.atan2(vector1[1], vector1[0]);
    let theta2 = Math.atan2(vector2[1], vector2[0]);
    if (theta1 < theta2) theta1 += 2 * Math.PI;
    let t = numeric.linspace(theta1, theta2, 10000);
    let x = t.map(angle => center[0] + r1 * Math.cos(angle));
    let y = t.map(angle => center[1] + r1 * Math.sin(angle));
    return {
        data: [{
            x: x,
            y: y,
            mode: 'lines',
            line: { color: color }
        }],
        layout: { yaxis: { scaleanchor: "x", scaleratio: 1 } }
    };
}

// 逆时针弧
function arc_inverse(center, point1, point2, color = 'blue') {
    let vector1 = [point1[0] - center[0], point1[1] - center[1]];
    let vector2 = [point2[0] - center[0], point2[1] - center[1]];
    let r1 = Math.sqrt(vector1[0] ** 2 + vector1[1] ** 2);
    let theta1 = Math.atan2(vector1[1], vector1[0]);
    let theta2 = Math.atan2(vector2[1], vector2[0]);
    if (theta2 < theta1) theta2 += 2 * Math.PI;
    let t = numeric.linspace(theta1, theta2, 10000);
    let x = t.map(angle => center[0] + r1 * Math.cos(angle));
    let y = t.map(angle => center[1] + r1 * Math.sin(angle));
    return {
        data: [{
            x: x,
            y: y,
            mode: 'lines',
            line: { color: color }
        }],
        layout: { yaxis: { scaleanchor: "x", scaleratio: 1 } }
    };
}

// 通过角度画弧
function arc_degree(center, radius, angle1, angle2, color = 'b') {
    if (angle1 < angle2) {
        let angle = numeric.linspace(angle1, angle2, 100000);
        let x = angle.map(a => center[0] + radius * Math.cos(a));
        let y = angle.map(a => center[1] + radius * Math.sin(a));
        return {
            data: [{
                x: x,
                y: y,
                mode: 'lines',
                line: { color: color }
            }],
            layout: { yaxis: { scaleanchor: "x", scaleratio: 1 } }
        };
    }
}