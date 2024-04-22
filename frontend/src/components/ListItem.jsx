const ListItem = ({ data, datatypes }) => {
  const resultList = [];
  datatypes &&
    datatypes.map((datapoint) => {
      if (datapoint === "runtime") {
        const runtimeSeconds = data[datapoint];
        const hours = Math.floor(runtimeSeconds / 3600);
        var remainingSeconds = runtimeSeconds - hours * 3600;
        const minutes = Math.floor(remainingSeconds / 60);
        remainingSeconds = remainingSeconds - minutes * 60;

        if (hours > 0) {
          resultList.push(`${hours}h ${minutes}m ${remainingSeconds}s`);
        } else {
          resultList.push(`${minutes}m ${remainingSeconds}s`);
        }
      } else if (datapoint === "player_name2") {
        if (data[datapoint]) resultList.push(data[datapoint]);
        else resultList.push(null);
      } else if (datapoint === "verification_date") {
        var re = /([A-Za-z])+, [0-9]+ [A-Za-z]+ 20[0-9][0-9]/g;
        resultList.push(`${(data[datapoint].match(re) || []).join("")}`);
      } else {
        resultList.push(data[datapoint]);
      }
    });
  return resultList.map((tableData, index) => {
    return <td key={index}>{tableData}</td>;
  });
};

export default ListItem;
