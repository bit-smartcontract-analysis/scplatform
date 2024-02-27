
function bindImportBtnClick(){
    $("#file_path-btn").on("click", function(){

        var file_path = $("input[name='file_path']").val();
        if(!file_path){
            alert("请先输入文件路径！");
            return;
        }
        // 通过js发送网络请求：ajax Async. JavaScript And XML (JSON)
        // Jinja2
        $.ajax({
            url: "/tools/docImport",
            method: "POST",
            data: {
                "file_path": file_path
            },
            success: function (res){
                var code = res.code;
                var fileCount = res.fileCount;
                var fileLanguages = res.fileLanguages;
                var message = res.message;
                if(code == 200){
                    if (fileCount !== null) {
                        $("#fileCount").text(fileCount);
                    } else {
                        alert("Unable to determine the file count.");
                    }
                    var fileLanguagesList = $("#fileLanguages");
                    fileLanguagesList.empty(); // Clear the existing list

                    for (var language in fileLanguages) {
                        var count = fileLanguages[language];
                        var listItem = $("<li>").text(language + ": " + count);
                        fileLanguagesList.append(listItem);
                    }
                }else{
                    $("#fileLanguages").text("0");
                    $("#fileCount").text("0");
                    alert(message);
                }
            },
            error: function(xhr, textStatus, error) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        })
    });

}


function updateCheckboxGrid(toolList) {
    var checkboxGrid = document.getElementById("checkbox-grid");
    checkboxGrid.innerHTML = "";

    for (var i = 0; i < toolList.length; i++) {
      var tool = toolList[i];

      var div = document.createElement("div");
      div.classList.add("form-check");

      var input = document.createElement("input");
      input.classList.add("form-check-input");
      input.type = "checkbox";
      input.id = tool;
      input.name = "selected-tools";
      input.value = tool;

      var label = document.createElement("label");
      label.classList.add("form-check-label");
      label.htmlFor = tool;
      label.textContent = tool;

      div.appendChild(input);
      div.appendChild(label);

      checkboxGrid.appendChild(div);
    }
  }


function bindProLangBtnClick(){
    var tbody = document.getElementById("tbodyContent"); //获取tbody对象
    $("#select_prolang-btn").on("click",function(event){
        var obj = document.getElementById("select-prolanguage").value;

        // 通过js发送网络请求：ajax Async. JavaScript And XML (JSON)
        // Jinja2
        $.ajax({
            url: "/tools/toolFilter",
            method: "POST",
            data: {
                "select-prolanguage": obj
            },
            success: function (res){
                updateCheckboxGrid(res.toolList);
            },
            error: function(xhr, status, error) {
                // Handle the error response if needed
            }
        })
        $("input[name='file_path']").val("");
    });
}

function buildTbody(data){
    var tbody = document.getElementById("tbodyContent"); //获取tbody对象
    //先清空tbody
    tbody.innerHTML = "";
    var libGoodsList = data;
    for (var i = 0; i < libGoodsList.length; i++) {
        var tr = document.createElement("tr"); //创建tr
        for (var name in libGoodsList[i]) {
            var td = document.createElement("td"); //创建td
            var value = libGoodsList[i][name];
            if (name == "id") { //对象字段：ID
                td.innerHTML = value;
            }
            else if (name == "barcode") { //对象字段：条形码
                td.innerHTML = value;
            }
            else if (name == "name") {  //对象字段：名称
                td.innerHTML = value;
            }
            else if (name == "shortName") {  //对象字段：简称
                td.innerHTML = value;
            }
            else if (name == "isAudit") {  //对象字段：是否审核
                if(value == false){
                    td.innerHTML = "未审核";
                }
                else td.innerHTML = "已审核";
            }
            else if (name == "isEnabled") {  //对象字段：是否启用
                if(value == false){
                    td.innerHTML = "停用";
                }
                else td.innerHTML = "启用";
            }
            else {
                continue;  //排除剩余的
            }
            tr.appendChild(td);  //附加到tr节点
        }
        tbody.appendChild(tr); //附加到tbody节点
    }
}

function timeImportBtnClick() {
    var selectedItems = $('#selected-items-container').text().trim().split(','); // Split the string into an array;
    var selectedItemsText = selectedItems.map(item => item.trim()).filter(item => item !== '');
    var fileCountText = $('#fileCount').text().trim();
    var fileCount = fileCountText !== '' ? parseInt(fileCountText) : 0;

    $.ajax({
        url: '/tools/countTimes',
        method: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({ selectedItems: selectedItems, fileCount : fileCount }),
        success: function(response) {
            var data = response.data;
            var timeContainer = $('#time-container');
            timeContainer.empty();

            data.forEach(function(item) {
              var listItem = $('<li>').text('工具名称: ' + item.name + ', 预计时间: ' + item.time);
              timeContainer.append(listItem);
            });

          // Show the time-container
          timeContainer.show();
        },
        error: function(xhr, textStatus, error) {
          console.log(xhr.status + ': ' + xhr.responseText);
        }
      });
  }

function redImportBtnClick() {
    $('#process-btn').click(function() {
        var progressBar = $('#progress-bar');
        var width = 0;
        var interval = setInterval(function() {
            width += 10;
            progressBar.css('width', width + '%');
            if (width >= 100) {
                clearInterval(interval);
                displayLogContent();
            }
        }, 1000);

        $.ajax({
            url: '/tools/process',
            type: 'POST',
            success: function(data) {
            var logData = data.log_data;

            // Make the logData accessible to the displayLogContent function
            window.logData = logData;
            }
        });
        });
  }

  // Function to display the log content
function displayLogContent() {
    var logContainer = $('#log-container');
    logContainer.empty();

    if (window.logData) {
      window.logData.forEach(function(logItem) {
        var listItem = $('<li>').text(logItem.name);

        if (logItem.extended) {
          var link = $('<a>').text('智能合约检测报告').attr('href', '#');

          link.click(function() {
            var url = '/tools/popup?name=' + encodeURIComponent(logItem.name) + '&content=' + encodeURIComponent(logItem.message);
            var popupWindow = window.open(url, 'Popup Window', 'width=400,height=300');
          });

          listItem.append(link);
        }

        logContainer.append(listItem);
      });
    }
}
const toolUrls = {
    'mythril': '/toolFunc/run/mythril',
    'oyente': '/toolFunc/run/oyente',
    'slither': '/toolFunc/run/slither',
    'conkas': '/toolFunc/run/conkas',
    'solhint': '/toolFunc/run/solhint',
    'confuzzius': '/toolFunc/run/confuzzius',
    'security': '/toolFunc/run/security',
    'sfuzz': '/toolFunc/run/sfuzz',
    'osiris': '/toolFunc/run/osiris',
    'honeybadger': '/toolFunc/run/honeybadger'

};

function executeToolBtnClick() {
    $('#execute-tool-btn').on("click", function() {
        const selectedTool = $('#item-type').val();
        const toolUrl = toolUrls[selectedTool];

        // You can now use toolUrl for further processing
        // For example, making an AJAX request to execute the selected tool
        $.ajax({
            url: toolUrl,
            method: 'GET',
            contentType: 'application/json',
            success: function(response) {
                if (response) {
                    console.log(response)
                    $('#message').html(response.message);
                    $('#exit_code').html('Exit Code: ' + response.exit_code);
                    $('#logs').html('Logs: ' + JSON.stringify(response.logs, null, 4));
                    $('#execution_time').html('Duration: ' + response.time);
                }
                else {
                    $('#message').html('No response found.');

                }
            }
        });
    });
}

function mutationObserver() {
    var selectedItemsContainer = document.getElementById('selected-items-container');
    var selectedItems = document.getElementById('selected-items');
    var monitor = document.getElementById('monitor');

    var observer = new MutationObserver(function(mutationsList) {
    for (var mutation of mutationsList) {
        if (mutation.type === 'childList') {
        selectedItems.textContent = selectedItemsContainer.textContent;
        // monitor.textContent = 'Selected items: ' + selectedItemsContainer.textContent;
        }
    }
    });

    var observerConfig = { childList: true };
    observer.observe(selectedItemsContainer, observerConfig);
}


//等网页文档所有元素加载完成后再执行
$(document).ready(function (){
    bindImportBtnClick();
    bindProLangBtnClick();
    executeToolBtnClick();
    // buildTbody();
    redImportBtnClick();

    $('#timeDetect-btn').click(function() {
        // Hide the time-container initially
        $('#time-container').hide();

        // Call the updateTimeContainer function
        timeImportBtnClick();
      });
});



