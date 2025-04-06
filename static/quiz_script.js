let currentQuestion = {};
let score = 0;
let questionCount = 0;

function startQuiz() {
  const topic = document.getElementById("topic").value;
  const difficulty = document.getElementById("difficulty").value;

  if (!topic) {
    alert("Please enter a topic!");
    return;
  }

  fetch("/start_quiz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, difficulty }),
  })
    .then((res) => res.json())
    .then((data) => {
      displayQuestion(data);
      document.getElementById("setup-section").classList.add("hidden");
      document.getElementById("quiz-section").classList.remove("hidden");
    })
    .catch((err) => console.error(err));
}

function displayQuestion(data) {
  currentQuestion = data;
  document.getElementById("question").innerText = data.question;
  const optionsDiv = document.getElementById("options");
  optionsDiv.innerHTML = "";

  data.options.forEach((option) => {
    const btn = document.createElement("button");
    btn.className =
      "block w-full p-2 border rounded bg-gray-200 hover:bg-gray-300";
    btn.innerText = option;
    btn.onclick = () => checkAnswer(btn, option);
    optionsDiv.appendChild(btn);
  });
}

function checkAnswer(btn, answer) {
  if (answer === currentQuestion.correct_answer) {
    btn.classList.add("bg-green-500", "text-white");
    score++;
  } else {
    btn.classList.add("bg-red-500", "text-white");
  }
  document
    .querySelectorAll("#options button")
    .forEach((b) => (b.disabled = true));
}

function nextQuestion() {
  if (++questionCount < 5) {
    startQuiz();
  } else {
    document.getElementById("quiz-section").classList.add("hidden");
    document.getElementById("score-section").classList.remove("hidden");
    document.getElementById("final-score").innerText = `Your Score: ${score}/5`;
  }
}
