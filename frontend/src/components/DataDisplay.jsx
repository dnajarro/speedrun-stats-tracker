import { useState, useEffect } from "react";
import TopTen from "./TopTen";
import Graph from "./Graph";
import style from "./DataDisplay-style.css";
import axios from "axios";

const DataDisplay = ({ application }) => {
  const apiURL = "http://127.0.0.1:4000";
  const [fastestTimeGraph, setFastestTimeGraph] = useState("");
  const [totalRunsGraph, setTotalRunsGraph] = useState("");
  const [allRuns, setAllRuns] = useState({});
  const [recentRuns, setRecentRuns] = useState({});
  const [topTens, setTopTens] = useState({});
  const [topTensCategories, setTopTenCategories] = useState([]);
  const [allRunsGameNames, setAllRunsGameNames] = useState([]);
  const [recentRunsGameNames, setRecentRunsGameNames] = useState([]);

  const topTensList = topTensCategories.map((category, index) => (
    <li key={index}>
      <TopTen
        gameName={topTens[category][0]["game_name"]}
        title={category}
        data={topTens[category]}
      ></TopTen>
    </li>
  ));

  const allRunsCountList = allRunsGameNames.map((gameName, index) => (
    <li key={index}>
      <h3>Total runs submitted for {gameName}:</h3>
      <p>{allRuns[gameName].length}</p>
    </li>
  ));

  const recentRunsCountList = recentRunsGameNames.map((gameName, index) => (
    <li key={index}>
      <h3>Total validated runs submitted for {gameName} since last update:</h3>
      <p>{recentRuns[gameName].length}</p>
    </li>
  ));

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [
          fastestTimeGraphResponse,
          totalRunsGraphResponse,
          allRunsResponse,
          recentRunsResponse,
          topTensResponse,
        ] = await Promise.all([
          axios.get(`${apiURL}/api/${application}/firstplace/graph`),
          axios.get(`${apiURL}/api/${application}/allruns/graph`),
          axios.get(`${apiURL}/api/${application}/allruns`),
          axios.get(`${apiURL}/api/${application}/recentruns`),
          axios.get(`${apiURL}/api/${application}/toptens`),
        ]);
        const allRunsGameNameList = Object.keys(allRunsResponse.data);
        const recentRunsGameNameList = Object.keys(recentRunsResponse.data);
        const topTensCategoriesList = Object.keys(topTensResponse.data);
        setFastestTimeGraph(fastestTimeGraphResponse.data["img"]);
        setTotalRunsGraph(totalRunsGraphResponse.data["img"]);
        setAllRuns(allRunsResponse.data);
        setRecentRuns(recentRunsResponse.data);
        setTopTens(topTensResponse.data);
        setAllRunsGameNames(allRunsGameNameList);
        setRecentRunsGameNames(recentRunsGameNameList);
        setTopTenCategories(topTensCategoriesList);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);
  return (
    <>
      <ul>{topTensList}</ul>
      <ul>{allRunsCountList}</ul>
      <ul>{recentRunsCountList}</ul>
      <div>
        <Graph image={fastestTimeGraph}></Graph>
        <Graph image={totalRunsGraph}></Graph>
      </div>
    </>
  );
};

export default DataDisplay;
