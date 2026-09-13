const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const optionsContainer = document.getElementById("options");
const correctOption = document.getElementById("correctOption");
const pollType = document.getElementById("pollType");
const correctBox = document.getElementById("correctBox");
const result = document.getElementById("result");

let options = ["", "", "", ""];


function renderOptions() {
  optionsContainer.innerHTML = "";

  options.forEach((value, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "option";

    const input = document.createElement("input");

    input.type = "text";
    input.placeholder = `گزینه ${index + 1}`;
    input.value = value;

    input.addEventListener("input", () => {
      options[index] = input.value;
      renderCorrectOptions();
    });

    const remove = document.createElement("button");

    remove.textContent = "×";
    remove.className = "remove";

    remove.onclick = () => {
      if (options.length <= 2) {
        tg.showAlert("حداقل دو گزینه لازم است.");
        return;
      }

      options.splice(index, 1);

      renderOptions();
      renderCorrectOptions();
    };

    wrapper.appendChild(input);
    wrapper.appendChild(remove);

    optionsContainer.appendChild(wrapper);
  });

  renderCorrectOptions();
}


function renderCorrectOptions() {
  const previous = correctOption.value;

  correctOption.innerHTML = "";

  options.forEach((value, index) => {
    const option = document.createElement("option");

    option.value = index;
    option.textContent =
      value.trim() || `گزینه ${index + 1}`;

    correctOption.appendChild(option);
  });

  if (
    previous !== "" &&
    Number(previous) < options.length
  ) {
    correctOption.value = previous;
  }
}


function updateTypeUI() {
  correctBox.style.display =
    pollType.value === "quiz"
      ? "block"
      : "none";
}


document.getElementById("addOption").onclick = () => {
  if (options.length >= 10) {
    tg.showAlert("حداکثر ۱۰ گزینه مجاز است.");
    return;
  }

  options.push("");

  renderOptions();
};


pollType.addEventListener(
  "change",
  updateTypeUI
);


document.getElementById("save").onclick = async () => {
  const question =
    document.getElementById("question").value.trim();

  const analysis =
    document.getElementById("analysis").value.trim();

  const postText =
    document.getElementById("postText").value.trim();


  if (!question) {
    tg.showAlert("سؤال را وارد کنید.");
    return;
  }


  const cleanOptions =
    options.map(x => x.trim());


  if (cleanOptions.some(x => !x)) {
    tg.showAlert("همه گزینه‌ها را کامل کنید.");
    return;
  }


  if (
    new Set(cleanOptions).size !==
    cleanOptions.length
  ) {
    tg.showAlert(
      "گزینه‌های تکراری مجاز نیستند."
    );

    return;
  }


  const payload = {
    question,
    options: cleanOptions,

    type: pollType.value,

    correct_option_id:
      pollType.value === "quiz"
        ? Number(correctOption.value)
        : null,

    analysis,
    post_text: postText,

    telegram_user:
      tg.initDataUnsafe?.user || null
  };


  try {
    const response = await fetch(
      "/api/questions",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify(payload)
      }
    );


    const data = await response.json();


    if (!response.ok) {
      throw new Error(
        data.detail || "خطا در ذخیره سؤال"
      );
    }


    result.textContent =
      `✅ سؤال ${data.content_id} ذخیره شد.`;

    result.className = "success";


    tg.HapticFeedback?.notificationOccurred(
      "success"
    );


    /*
     * ساخت دکمه انتشار
     */

    const publishButton =
      document.createElement("button");

    publishButton.textContent =
      "📤 انتشار در تلگرام";

    publishButton.className =
      "publish-button";


    publishButton.onclick =
      async () => {

        publishButton.disabled = true;

        publishButton.textContent =
          "⏳ در حال انتشار...";


        try {

          const publishResponse =
            await fetch(
              `/api/questions/${data.content_id}/publish`,
              {
                method: "POST"
              }
            );


          const publishData =
            await publishResponse.json();


          if (!publishResponse.ok) {
            throw new Error(
              publishData.detail ||
              "خطا در انتشار"
            );
          }


          result.textContent =
            `✅ ${data.content_id} با موفقیت در تلگرام منتشر شد.`;

          result.className =
            "success";


          publishButton.textContent =
            "✅ منتشر شد";


          tg.HapticFeedback?.notificationOccurred(
            "success"
          );

        } catch (error) {

          publishButton.disabled = false;

          publishButton.textContent =
            "📤 انتشار در تلگرام";


          result.textContent =
            `❌ ${error.message}`;

          result.className =
            "error";


          tg.HapticFeedback?.notificationOccurred(
            "error"
          );
        }
      };


    /*
     * حذف دکمه قبلی در صورت وجود
     */

    const oldButton =
      document.getElementById(
        "publishButton"
      );

    if (oldButton) {
      oldButton.remove();
    }


    publishButton.id =
      "publishButton";


    /*
     * اضافه کردن دکمه به صفحه
     */

    result.parentNode.appendChild(
      publishButton
    );


  } catch (error) {

    result.textContent =
      `❌ ${error.message}`;

    result.className =
      "error";
  }
};


renderOptions();
updateTypeUI();
