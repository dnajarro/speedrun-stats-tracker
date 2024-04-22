import "./Graph-style.css";

const Graph = ({ image }) => {
  return <img src={`data:image/png;base64,${image}`} alt="graph"></img>;
};

export default Graph;
