import React, { useState } from "react";
import Button from "./Button";
import SelectTable from "./SelectTable";
import FormController from "../components/forms/FormController";
import { api } from "../services/api.js";

const ActionWindow = ({ setData, setTableName }) => {
  const [from_table, setFromTable] = useState("/contents");
  const [to_table, setToTable] = useState("/contents");
  const [body, setBody] = useState([]);

  function handleRequest() {
    api
      .get(from_table, {
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
      })
      .catch((error) => console.log(error));
  }

  function handleAddition() {
    api
      .post(to_table, JSON.parse(body), {
        headers: {
          Authorization:
            "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
        },
      })
      .then((res) => window.alert(res))
      .catch((error) => console.log(error));
  }

  return (
    <div className="auth-inner">
      <SelectTable setTable={setFromTable} setTableName={setTableName} />
      <Button label="Get available rows" onClick={handleRequest} />
      <SelectTable setTable={setToTable} setTableName={setTableName} />
      <FormController
        to_table={to_table}
        setBody={setBody}
        handleAddition={handleAddition}
      />
    </div>
  );
};

export default ActionWindow;
