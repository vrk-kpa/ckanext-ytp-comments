this.ckan.module('follow-or-mute', function (jQuery) {
  return {
    /* An object of module options */
    options: {
      /* Content can be overriden by setting data-module-content to a
       * *translated* string inside the template, e.g.
       *
       *     <a href="..."
       *        data-module="confirm-action"
       *        data-module-content="{{ _('Are you sure?') }}">
       *    {{ _('Delete') }}
       *    </a>
       */
      content: '',

      /* This is part of the old i18n system and is kept for backwards-
       * compatibility for templates which set the content via the
       * `i18n.content` attribute instead of via the `content` attribute
       * as described above.
       */
      i18n: {
        content: '',
      },

      template: [
        '<div class="modal fade">',
        '<div class="modal-dialog">',
        '<div class="modal-content">',
        '<div class="modal-header">',
        '<button type="button" class="close" data-dismiss="modal">×</button>',
        '<h3 class="modal-title"></h3>',
        '</div>',
        '<div class="modal-body"></div>',
        '<div class="modal-footer">',
        '<button class="btn btn-primary"></button>',
        '</div>',
        '</div>',
        '</div>',
        '</div>'
      ].join('\n')
    },

    /* Sets up the event listeners for the object. Called internally by
     * module.createInstance().
     *
     * Returns nothing.
     */
    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },

    /* Presents the user with a modal dialogue to notify them that a
     * thread has been followed or muted
     *
     * Returns nothing.
     */
    displayModal: function () {
      this.sandbox.body.append(this.createModal());
      this.modal.modal('show');

      // Center the modal in the middle of the screen.
      this.modal.css({
        'margin-top': this.modal.height() * -0.5,
        'top': '50%'
      });
    },

    /* Creates the modal dialog, attaches event listeners and localised
     * strings.
     *
     * Returns the newly created element.
     */
    createModal: function () {
      if (!this.modal) {
        var element = this.modal = jQuery(this.options.template);
        element.on('click', '.btn-primary', this._onClose);
        element.modal({show: false});

        element.find('.modal-title').text(this.options.title);

        var content = this.options.content ||
                      this.options.i18n.content || /* Backwards-compatibility */
                      this._('Thread followed.');
        element.find('.modal-body').text(content);
        element.find('.btn-primary').text(this._('Close'));
      }
      return this.modal;
    },

    /* Event handler that displays the confirm dialog */
    _onClick: function (event) {
      event.preventDefault();
      var action = 'follow';
      var inverse = 'mute';
      if (this.options.action === 'mute') {
          action = 'mute';
          inverse = 'follow';
      }
      var content_type = this.options.content_type;
      var thread_id = this.options.thread_id;
      var comment_id = this.options.comment_id;
      var element = this;
      this.options.title = jQuery(element.el).attr('title');
      jQuery.get('/comments/' + (thread_id ? thread_id : comment_id) + '/' + action, function() {
        jQuery(element.el).addClass('hidden');
        jQuery(element.el).parent().find('.comments-' + inverse + (thread_id ? '' : '-thread')).removeClass('hidden');
        if (!comment_id) {
          jQuery('.comments-follow-thread').addClass('hidden');
          jQuery('.comments-mute-thread').removeClass('hidden');
        }
      })
      .fail(function() {
        element.options.content = 'An error occurred while attempting to ' + action + ' this ' + (thread_id ? content_type : 'thread') + '.';
      });
      this.displayModal();
      return false;
    },

    /* Event handler for the close event */
    _onClose: function (event) {
      this.modal.modal('hide');
    }
  };
});
