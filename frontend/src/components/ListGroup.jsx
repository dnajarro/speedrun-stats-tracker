import ListItem from "./ListItem";

const ListGroup = ({ data, datatypes }) => {
  const listItems =
    data &&
    data.map((datapoint, index) => (
      <li key={index}>
        <ListItem data={data[index]} datatypes={datatypes}></ListItem>
      </li>
    ));
  return <ol>{listItems}</ol>;
};

export default ListGroup;
