import ListItem from "./ListItem";
import style from "./ListGroup-style.css";

const ListGroup = ({ data, datatypes }) => {
  const listItems =
    data &&
    data.map((datapoint, index) => (
      <li key={index} className="list-item">
        <ListItem data={data[index]} datatypes={datatypes}></ListItem>
      </li>
    ));
  return <ol>{listItems}</ol>;
};

export default ListGroup;
