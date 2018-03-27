/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

// Handle PublicToggle button on profile_detail
$(document).ready(function(){

    var $myForm = $('.ajax-public-toggle-form')
    $myForm.change(function(event){
        // event.preventDefault()
        var $formData = $(this).serialize()
        var $endpoint = $myForm.attr('data-url') || window.location.href // or set your own url

        // if change prefs to all none, auto change public to false
        $.ajax({
            method: "POST",
            url: $endpoint,
            data: $formData,
            success: handleFormSuccess,
            error: handleFormError,
        })
    })

    function handleFormSuccess(data, textStatus, jqXHR){
        // no need to do anything here
        console.log(data)
        console.log(textStatus)
        console.log(jqXHR)
        // $myForm[0].reset(); // reset form data
    }

    function handleFormError(jqXHR, textStatus, errorThrown){
        // on error, reset form. raise valifationerror
        $('#public_toggle_form_errors').text(jqXHR["responseJSON"]["public"]);
        $('#public_toggle_form_errors').show();
        console.log(jqXHR)
        console.log(textStatus)
        console.log(errorThrown)
        $myForm[0].reset(); // reset form data

        // console.log(errors)
    }
})

$(document).ready(function(){

    var $myButton = $('.pairing-CTA-btn')
    $myButton.click(function(event){
        event.preventDefault()
        // var buttonLocation = $(this).attr('href')
        var $buttonData = $(this).serialize()
        var $endpoint = $myButton.attr('data-check-public-url') || window.location.href // or set your own url

        $.ajax({
            method: "POST",
            url: $endpoint,
            data: $buttonData,
            success: handleSuccess,
            error: handleError,
        })
    })

    function handleSuccess(data, textStatus, jqXHR){
        // No need to do anything here. Allow link click.
        console.log(data)
        console.log(textStatus)
        console.log(jqXHR)
        var buttonLocation = $('.pairing-CTA-btn').attr('href')

        window.location = buttonLocation

    }

    function handleError(jqXHR, textStatus, errorThrown){
        console.log(jqXHR)
        console.log(textStatus)
        console.log(errorThrown)
        $('#public_check_errors').text(jqXHR["responseJSON"]["message"]);
        $('#public_check_errors').show();
        // on error, prevent default, bring up errors
        // event.preventDefault()
        // $('.pairing-CTA-btn-errors').text("YOU SHALL NOT CLICK BUTTON");
        // $('.pairing-CTA-btn-errors').show();

    }
})
