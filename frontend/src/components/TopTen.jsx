import ListTitle from "./ListTitle";
import ListGroup from "./ListGroup";
import style from "./TopTen-style.css";

const TopTen = ({ gameName, title, data }) => {
  const newGameName = gameName.replace(/(\s)/g, "-");
  const listGroupClassName = `ListGroup ${newGameName}`;
  // alert(newGameName);
  return (
    <>
      <div className="title">
        <ListTitle title={title}></ListTitle>
      </div>
      <div className={listGroupClassName}>
        <ListGroup
          data={data}
          datatypes={[
            "player_name1",
            "player_name2",
            "runtime",
            "verification_date",
          ]}
        ></ListGroup>
      </div>
    </>
  );
};
export default TopTen;
