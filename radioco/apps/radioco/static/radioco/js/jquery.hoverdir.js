/**
 * jQuery.Hoverdir
 *
 * Modified version of https://github.com/codrops/DirectionAwareHoverEffect
 *
 * Modifications:
 * - Removed CSS3 transitions and Modernizr requirements.
 * - Applied CSS classes for improved flexibility via CSS.
 *
 * @copyright  2015 WebMan - Oliver Juhas, www.webmandesign.eu
 *
 * @link  https://github.com/webmandesign/jquery.hoverdir
 *
 * @version  1.1.2
 */

/**
 * jquery.hoverdir.js v1.1.2
 * http://www.codrops.com
 *
 * Licensed under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Copyright 2012, Codrops
 * http://www.codrops.com
 */

( function( factory ) {



	'use strict';



	if ( typeof define === 'function' && define.amd ) {
		define( ['jquery'], factory );
	} else if ( typeof exports !== 'undefined' ) {
		module.exports = factory( require( 'jquery' ) );
	} else {
		factory( jQuery );
	}



} )( function( $ ) {



	'use strict';



	function Hoverdir( element, options ) {

		this.$el = $( element );

		// Set options

		this.options = $.extend( true, {}, this.defaults, options );

		// All classes that plugin generates

		this.allClasses = {
				from : this.options.fromPrefix + 'top ' + this.options.fromPrefix + 'right ' + this.options.fromPrefix + 'bottom ' + this.options.fromPrefix + 'left',
				to   : this.options.toPrefix + 'top ' + this.options.toPrefix + 'right ' + this.options.toPrefix + 'bottom ' + this.options.toPrefix + 'left'
			};

		// Load the events

		this._loadEvents();

	} // /Hoverdir



	Hoverdir.prototype = {

		defaults : {
			fromPrefix : 'out-',
			toPrefix   : 'in-'
		},

		constructor : Hoverdir,



		_loadEvents : function() {

			this.$el.on( 'mouseenter.hoverdir mouseleave.hoverdir', $.proxy( function( event ) {

				var fromPrefix = this.options.fromPrefix,
				    toPrefix   = this.options.toPrefix,
				    direction  = this._getDir( { x : event.pageX, y : event.pageY } ),
				    CSSclass   = this._getClass( direction );

				if ( event.type === 'mouseenter' ) {

					this.$el
						.removeClass( this.allClasses.from )
						.addClass( toPrefix + CSSclass )
						.siblings()
							.removeClass( this.allClasses.to );

				} else {

					this.$el
						.removeClass( this.allClasses.to )
						.addClass( fromPrefix + CSSclass )
						.siblings()
							.removeClass( this.allClasses.from );

				}

			}, this ) );

		},



		/**
		 * Get the direction when the event is triggered.
		 * Credits : http://stackoverflow.com/a/3647634
		 *
		 * @param  {Object} coordinates
		 *
		 * @return  {Interger}
		 */
		_getDir : function( coordinates ) {

			// The width and height of the current div

			var w = this.$el.width(),
			    h = this.$el.height(),

			    // Calculate the x and y to get an angle to the center of the div from that x and y.
			    // Gets the x value relative to the center of the DIV and "normalize" it

			    x = ( coordinates.x - this.$el.offset().left - ( w / 2 ) ) * ( w > h ? ( h / w ) : 1 ),
			    y = ( coordinates.y - this.$el.offset().top  - ( h / 2 ) ) * ( h > w ? ( w / h ) : 1 ),

			    // The angle and the direction from where the mouse came in/went out clockwise (TRBL=0123);
			    // first calculate the angle of the point,
			    // add 180 deg to get rid of the negative values
			    // divide by 90 to get the quadrant
			    // add 3 and do a modulo by 4 to shift the quadrants to a proper clockwise TRBL (top/right/bottom/left).

			    direction = Math.round( ( ( ( Math.atan2( y, x ) * ( 180 / Math.PI ) ) + 180 ) / 90 ) + 3 ) % 4;

			return direction;

		},



		/**
		 * Return a class based on cursor direction
		 */
		_getClass : function( direction ) {

			var CSSclass;

			switch( direction ) {
				case 0:
					CSSclass = 'top';
					break;
				case 1:
					CSSclass = 'right';
					break;
				case 2:
					CSSclass = 'bottom';
					break;
				case 3:
					CSSclass = 'left';
					break;
			}

			return CSSclass;

		},



		/**
		 * Setting options for plugin binding
		 */
		setOptions : function (options) {

			this.options = $.extend( true, {}, this.defaults, this.options, options );

		},



		/**
		 * Unbinds the plugin
		 */
		destroy : function () {

			this.$el.off( 'mouseenter.hoverdir mouseleave.hoverdir' );
			this.$el.data( 'hoverdir', null );

		},



		/**
		 * Bind the plugin
		 */
		rebuild : function (options) {

			if ( typeof options === 'object' ) {
				this.setOptions( options );
			}

			this._loadEvents();

		}

	};



	$.fn.hoverdir = function( option, parameter ) {

		return this.each( function() {

			var data    = $( this ).data( 'hoverdir' ),
			    options = typeof option === 'object' && option;

			// Initialize hoverdir.

			if ( ! data ) {
				data = new Hoverdir( this, options );
				$( this ).data( 'hoverdir', data );
			}

			// Call hoverdir method.

			if ( typeof option === 'string' ) {
				data[ option ]( parameter );

				if ( option === 'destroy' ) {
					$( this ).data( 'hoverdir', false );
				}
			}

		} );

	};



	$.fn.hoverdir.Constructor = Hoverdir;



} );