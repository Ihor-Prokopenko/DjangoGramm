$(document).ready(function() {
    $('.like-form').submit(function(e) {
        e.preventDefault();
        const post_id = $(this).attr('id');
        const likeBtn = $(`.like-btn${post_id}`);
        const likeImg = likeBtn.find('img');

        const url = $(this).attr('action');

        const likeCount = $(`.like-count${post_id}`);
        let likes = parseInt(likeCount.text());

        likeBtn.addClass('disabled');

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'post_id': post_id,
            },
            success: function(response) {
                if (response.value === 'added') {
                    likeImg.attr('src', '/static/img/favorite_on.png');
                    console.log('added like')
                }
                else {
                    likeImg.attr('src', '/static/img/favorite_off.png');
                    console.log('removed like')
                }
                likeCount.text(response.likes_num);
            },
            error: function(response) {
                console.log('error', response);
                likeBtn.removeClass('disabled');
            }
        });
    });

    $('.post-save-form').submit(function(e) {
        e.preventDefault();

        const form = $(this);
        const postIdField = form.find('input[name="post_id"]');
        const postId = postIdField.val();
        const saveBtn = $(`.save-btn${postId}`);
        const saveImg = saveBtn.find('img');
        const url = $(this).attr('action');

        saveBtn.addClass('disabled');

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'post_id': postId,
            },
            success: function(response) {
                if (response.value === 'saved') {
                    saveImg.attr('src', '/static/img/pin_on.png');
                    console.log('saved post')
                }
                else {
                    saveImg.attr('src', '/static/img/pin_off.png');
                    console.log('unsaved post')
                }
                saveBtn.removeClass('disabled');
            },
            error: function(response) {
                console.log('error', response);
                saveBtn.removeClass('disabled');
            }
        });
    });

    $('.follow-form').submit(function(e) {
        e.preventDefault();

        const form = $(this);
        const profileIdField = form.find('input[name="profile_id"]');
        const profileId = profileIdField.val();

        const followersCountElement = document.getElementById('followers-count');
        const followersCount = followersCountElement.textContent;

        const url = $(this).attr('action');


        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'profile_id': profileId,

            },
            success: function(response) {
                if (response.action === 'followed') {
                    $(`.follow-btn${profileId}`).text('Unfollow')
                    followersCountElement.textContent = response.followers;
                }

                 else {
                    $(`.follow-btn${profileId}`).text('Follow')
                    followersCountElement.textContent = response.followers;
                 }
            },


        });

    });

});
