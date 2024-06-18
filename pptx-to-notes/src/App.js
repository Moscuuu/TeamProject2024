import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [notes, setNotes] = useState("");
  const [questions, setQuestions] = useState([]);
  const [showAnswers, setShowAnswers] = useState([]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    setNotes(data.notes);
  };

  const handleGenerateQuestions = async () => {
    const response = await fetch('http://127.0.0.1:5000/generate_questions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ notes }),
    });
    const data = await response.json();
    setQuestions(data.questions);
    setShowAnswers(new Array(data.questions.length).fill(false));
  };

  const handleToggleAnswer = (index) => {
    const newShowAnswers = [...showAnswers];
    newShowAnswers[index] = !newShowAnswers[index];
    setShowAnswers(newShowAnswers);
  };

  return (
    <div className="App">
      <h1>PPTX to Notes</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".pptx" required />
        <button type="submit">Generate Notes</button>
      </form>
      {notes && (
        <>
          <h2>Generated Notes:</h2>
          <pre>{notes}</pre>
          <button onClick={handleGenerateQuestions}>Generate Questions</button>
          <h2>Generated Questions:</h2>
          <ul>
            {questions.map((qna, index) => (
              <li key={index}>
                <strong>Q: {qna.question}</strong>
                <button onClick={() => handleToggleAnswer(index)}>
                  {showAnswers[index] ? 'Hide Answer' : 'Show Answer'}
                </button>
                {showAnswers[index] && <p>A: {qna.answer}</p>}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;