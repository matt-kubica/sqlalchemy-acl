import React, { useState } from "react";
import Table from "./Table";
import Button from "./Button";
import { api } from "../services/api.js";

const TablePage = () => {
  const [data, setData] = useState([]);

  if (data.length === 0) {
    return (
      <div className="auth-wrapper">
        <Button label="Get available rows" onClick={handleClick} />
      </div>
    );
  }

  function handleClick() {
    setData([{ att1: "value" }]);
    api
      .get("/exemplary-object", {
        headers: {
          Authorization:
            "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
        },
      })
      .then((res) => {
        if (res.data.length === 0) {
          window.alert(
            "The table you wanted to fetch is either empty, or you don't have access to any of its rows"
          );
        }
        setData(res.data);
      });
  }

  return (
    <div className="table-wrapper">
      <Table name={"Mati"} data={data} />
    </div>
  );
};

export default TablePage;
