const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  const analyze = env && env.analyze;

  return {
    entry: './src/widget.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'chat-widget.js',
      library: 'ANZxChatWidget',
      libraryTarget: 'umd',
      globalObject: 'this'
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: [
                ['@babel/preset-env', {
                  targets: {
                    browsers: ['> 1%', 'last 2 versions', 'ie >= 11']
                  },
                  modules: false
                }]
              ]
            }
          }
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        }
      ]
    },
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction,
              drop_debugger: isProduction,
              pure_funcs: isProduction ? ['console.log', 'console.info'] : []
            },
            mangle: {
              reserved: ['ANZxChatWidget']
            },
            format: {
              comments: false
            }
          },
          extractComments: false
        })
      ]
    },
    plugins: [
      ...(analyze ? [new BundleAnalyzerPlugin()] : [])
    ],
    resolve: {
      extensions: ['.js', '.json']
    },
    performance: {
      maxAssetSize: 50000, // 50KB limit for production
      maxEntrypointSize: 50000,
      hints: isProduction ? 'warning' : 'error'
    },
    devtool: isProduction ? false : 'source-map'
  };
};