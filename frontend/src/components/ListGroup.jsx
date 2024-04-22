import ListItem from "./ListItem";
import "./ListGroup-style.css";

const ListGroup = ({ data, datatypes }) => {
  const listItems =
    data &&
    data.map((datapoint, index) => (
      <tr key={index}>
        <ListItem
          key={index}
          data={data[index]}
          datatypes={datatypes}
        ></ListItem>
      </tr>
    ));
  return (
    <table>
      <thead>
        <tr>
          <th>Player Name 1</th>
          <th>Player Name 2</th>
          <th>Time</th>
          <th>Verification date</th>
        </tr>
      </thead>
      <tbody>{listItems}</tbody>
    </table>
  );
};

export default ListGroup;
