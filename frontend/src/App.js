import "./App.css";
import DataDisplay from "./components/DataDisplay";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <DataDisplay application={"flask"}></DataDisplay>
      </header>
    </div>
  );
}

export default App;
