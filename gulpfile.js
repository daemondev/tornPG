var gulp = require('gulp');
var react = require('gulp-react');

gulp.task('default', function () {
    return gulp.src('static/jsx/template.jsx')
        .pipe(react())
        .pipe(gulp.dest('static/js/react.app.js'));
});
