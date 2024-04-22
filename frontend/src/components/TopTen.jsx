import ListTitle from "./ListTitle";
import ListGroup from "./ListGroup";
import "./TopTen-style.css";

const TopTen = ({ gameName, title, data }) => {
  var backgroundImage;
  switch (gameName) {
    case "Super Mario Odyssey":
      backgroundImage = (
        <img src={require("../res/smo_logo.png")} alt="smo_img"></img>
      );
      break;
    case "Spyro the Dragon":
      backgroundImage = (
        <img
          src={require("../res/spyro_logo_image.webp")}
          alt="spyro_img"
        ></img>
      );
      break;
    case "Lies of P":
      backgroundImage = (
        <img
          src={require("../res/lies_of_p_logo.webp")}
          alt="lies_of_p_img"
        ></img>
      );
      break;
    default:
      backgroundImage = (
        <img
          src={require("../res/elden_ring_logo_image.webp")}
          alt="elden_ring_img"
        ></img>
      );
  }
  return (
    <>
      <div className="title">
        <ListTitle title={title}></ListTitle>
      </div>
      <div className="group-container">
        <div className="background-image">{backgroundImage}</div>
        <div className="list-group">
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
      </div>
    </>
  );
};
export default TopTen;
