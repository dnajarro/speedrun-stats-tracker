const Graph = ({ image }) => {
  return <img src={`data:image/png;base64,${image}`}></img>;
};

export default Graph;