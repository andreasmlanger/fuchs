function display(result) {
    document.getElementById('loader').style.display = 'none';
    displayMessage(result.message, result.alert)

    if (result.bokeh && result.bokeh2) {
        $("#bokeh").html(result.bokeh);
        $("#bokeh2").html(result.bokeh2);
    } else {
        $("#bokeh").html("");
        $("#bokeh2").html("");
    }
    if (result.table) {
        data = JSON.parse(result.table)
        $table.bootstrapTable('load', data);
        symbols = data.map(row => row['symbol']);
    } else {
        data = ''
    }
}

function displayMessage(message, alert) {
    if (message && alert) {
        $("#message").html('<div class="alert alert-' + alert + '">' + message + '</div>')
        window.setTimeout(function() {
            $(".alert").fadeTo(500, 0).slideUp(500, function(){
                $(this).remove();
            });
        }, 2000);
    }
}

function searchYahoo() {
    var name = document.getElementById('name-input').value.trim()
    if (name) {
        window.open('https://de.finance.yahoo.com/lookup?s=' + name)
    } else {
        window.open('https://de.finance.yahoo.com/')
    }
}

function highlight(x, color) {
    if (color == 'green') {
        document.getElementById(x).style.background = '#d4edda'
    } else if (color == 'red') {
        document.getElementById(x).style.background = '#f8d7da'
    } else if (color == 'yellow') {
        document.getElementById(x).style.background = '#fff3cd'
    } else {
        document.getElementById(x).style.background = '#f1f1f1'
    }
}

function submit_ajax(url, ajax_data) {
    document.getElementById('loader').style.display = 'inline-block';
    $.ajax({
        type: 'POST',
        url: url,
        data: Object.assign({}, ajax_data, {'csrfmiddlewaretoken': CSFRtoken}),
        success: function(result){
            display(result)
            updateTable()
        }
    });
}

function updateTable() {
    if (data.length > 0) {
        document.getElementById('stockTable').style.display = "block";
        document.getElementById('noStocksText').style.display = "none"
    } else {
        document.getElementById('stockTable').style.display = "none";
        document.getElementById('noStocksText').style.display = "block"
    }
}

function dateFormatter(value, row, index) {
    var d = new Date(value),
    month = '' + (d.getMonth() + 1),
    day = '' + d.getDate(),
    year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

var formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'EUR',
});

function euroColorFormatter(value, row, index) {
    if (value < 0) {
        return '<span style="color: red">' + formatter.format(value) + '</span>'
    } else {
        return '<span style="color: green">+' + formatter.format(value) + '</span>'
    }
}

function euroFormatter(value, row, index) {
    return formatter.format(value)
}

function percentageFormatter(value, row, index) {
    var str = (Math.round((value - 1) * 1000) / 10).toString()
    if (!str.includes('.')) {
        str = str + '.0'
    }
    if (value < 1) {
        return '<span style="color: red">' + str + '%</span>'
    } else {
        return '<span style="color: green">+' + str + '%</span>'
    }
}

function footerTodayPercentageFormatter(data) {
    var value_yesterday = data.map(function (row) {
        return +row['value'] / row['return_yesterday']
    }).reduce(function (sum, i) {
        return sum + i
    }, 0)

    var total_value = data.map(function (row) {
        return +row['value']
    }).reduce(function (sum, i) {
        return sum + i
    }, 0)

    return percentageFormatter(total_value / value_yesterday)
}

function footerOverallPercentageFormatter(data) {
    var total_investment = data.map(function (row) {
        return +row['investment']
    }).reduce(function (sum, i) {
        return sum + i
    }, 0)

    var total_value = data.map(function (row) {
        return +row['value']
    }).reduce(function (sum, i) {
        return sum + i
    }, 0)

    return percentageFormatter(total_value / total_investment)
}

function footerSumFormatter(data) {
    var field = this.field
    var sum = data.map(function (row) {
        return +row[field]
    }).reduce(function (sum, i) {
        return sum + i
    }, 0)

    if (field == 'profit') {
        return euroColorFormatter(sum)
    } else {
        return euroFormatter(sum)
    }
}

function downloadStocks(name) {
    document.getElementById("loader").style.display = "block"
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState === 4 && xhttp.status === 200) {
            var a = document.createElement('a');
            a.href = window.URL.createObjectURL(xhttp.response);
            a.download = name + ".xlsx";
            a.style.display = 'none';
            document.body.appendChild(a);
            document.getElementById("loader").style.display = "none"
            displayMessage('Download successful!', 'success')
            return a.click();
        }
    };
    xhttp.open("POST", "");
    xhttp.setRequestHeader("X-CSRFToken", CSFRtoken);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.responseType = 'blob';
    xhttp.send();
}

$('#chooseFileName').on('change',function(){
    var fileInput = document.getElementById('chooseFileName');
    var fileList = []

    for (var i = 0; i < fileInput.files.length; i++) {
        fileList.push(fileInput.files[i].name)
    }

    if (fileList.length === 1) {
        var fileListString = fileList[0]
    } else if (fileList.length === 2) {
        var fileListString = fileList.join(', ')
    } else {
        var fileListString = fileList[0] + ' + ' + (fileList.length - 1) + ' more files'
    }

    $(this).next('.custom-file-label').html(fileListString);

    $("#uploadForm").submit()
})

$("#uploadForm").on('submit', function(e){
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: new FormData(this),
        contentType: false,
        cache: false,
        processData:false,
        beforeSend: function(){
            document.getElementById("loader").style.display = "inline-block";
        },
        success: function(result){
            document.getElementById("loader").style.display = "none";
            if (result == 'No valid file!' || result == 'Data has already been uploaded!') {
                $("#result").html('<div class="alert alert-warning"><button type="button" class="close">×</button>' + result + '</div>')
            } else {
                display(result)
                updateTable()
            }
            window.setTimeout(function () {
             $(".alert").fadeTo(500, 0).slideUp(500, function () {
                     $(this).remove();
                 });
             }, 2000);

             $('.alert .close').on("click", function (e) {
                 $(this).parent().fadeTo(500, 0).slideUp(500);
             });
        }
    });
});

function scrollDown() {
    window.scrollBy({
        top: document.body.scrollHeight,
        behavior : "smooth"
    })
}

function isMobile() {
  let check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
};

$(function () {
    initTable()
    window.scrollBy({
        top: document.body.scrollHeight,
        behavior : "smooth"
    })
    $('[data-toggle="tooltip"]').tooltip({trigger : 'hover'})
})
