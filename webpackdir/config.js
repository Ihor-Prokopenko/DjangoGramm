const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');

module.exports = {
    entry: './src/js/index.js',
    mode: 'development',
    output: {
        filename: 'index.js',
        path: __dirname + '/../static/js',
    },
    module: {
        rules:[
            {
                test:/\.(scss)$/,
                use: [
                MiniCssExtractPlugin.loader,
                'css-loader',
                'sass-loader',
                ]
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '../css/index.css',
            filename: '../css/DG_styles.css',
        }),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
    ]
};
