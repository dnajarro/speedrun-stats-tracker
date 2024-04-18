import ListTitle from "./ListTitle";
import ListGroup from "./ListGroup";

const TopTen = ({ title, data }) => {
  return (
    <>
      <div>
        <ListTitle title={title}></ListTitle>
      </div>
      <div>
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
