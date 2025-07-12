import React from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register necessary Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function GraphPage({ graphType, data }) {
  // Convert the input data to Chart.js compatible format

  const chartData = {
    labels: Object.values(data)[0]?.x_values || [], // Use the x_values from the first data set as labels
    datasets: Object.entries(data).map(([key, value]) => ({
      label: `Channel ${key} Graph`,
      data: value.y_values,
      fill: false,
      backgroundColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`, // Random color for each graph
      borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`, // Random color for each graph
      borderWidth: 1,
    })),
  };

  // Dynamically render the selected graph type
  const options = {
    responsive: true,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Bins', // Label for X axis
        },
      },
      y: {
        title: {
          display: true,
          text: 'Event counts', // Label for Y axis
        },
      },
    },
  };

  // Dynamically render the selected graph type with options
  const renderGraph = () => {
    switch (graphType) {
      case 'line':
        return <Line data={chartData} options={options} />;
      case 'bar':
        return <Bar data={chartData} options={options} />;
      case 'pie':
        return <Pie data={chartData} />;
      default:
        return <div>Graph type not supported</div>;
    }
  };


  return <div>{renderGraph()}</div>;
}

export default GraphPage;
