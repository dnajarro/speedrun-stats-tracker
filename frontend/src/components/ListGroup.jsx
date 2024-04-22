import ListItem from "./ListItem";
import style from "./ListGroup-style.css";

const ListGroup = ({ data, datatypes }) => {
  var hasPlayer2 = false;
  for (var i = 0; i < data.length; i++) {
    if (data[i]["player_name2"]) {
      hasPlayer2 = true;
      break;
    }
  }
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
