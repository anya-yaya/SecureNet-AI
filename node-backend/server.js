require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const axios = require("axios");

const app = express();

app.use(cors());
app.use(express.json());


// MongoDB Connect
mongoose.connect(process.env.MONGO_URI)
.then(() => console.log("MongoDB Connected"))
.catch(err => console.log(err));


// Schema
const ScanSchema = new mongoose.Schema({
    text: String,
    result: String,
    createdAt: {
        type: Date,
        default: Date.now
    }
});

const Scan = mongoose.model("Scan", ScanSchema);


// Home Route
app.get("/", (req,res)=>{
    res.send("Node Backend Running");
});


// Scan Route
app.post("/scan", async (req,res)=>{

    try{

        const text = req.body.text;

        // Call FastAPI
        const response = await axios.post(
            "http://127.0.0.1:8000/predict",
            { text:text }
        );

        const result = response.data.result;

        // Save DB
        await Scan.create({
            text,
            result
        });

        res.json({
            text,
            result
        });

    }catch(error){
        res.status(500).json({
            error:"Server Error"
        });
    }

});


// History Route
app.get("/history", async(req,res)=>{

    const data = await Scan.find().sort({createdAt:-1});

    res.json(data);

});


app.listen(5000, ()=>{
    console.log("Server Running on Port 5000");
});