<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInitae7ffda9c382bef67838ac0ea2221b23
{
    public static $prefixLengthsPsr4 = array (
        'P' => 
        array (
            'PhpParser\\' => 10,
        ),
    );

    public static $prefixDirsPsr4 = array (
        'PhpParser\\' => 
        array (
            0 => __DIR__ . '/..' . '/nikic/php-parser/lib/PhpParser',
        ),
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixLengthsPsr4 = ComposerStaticInitae7ffda9c382bef67838ac0ea2221b23::$prefixLengthsPsr4;
            $loader->prefixDirsPsr4 = ComposerStaticInitae7ffda9c382bef67838ac0ea2221b23::$prefixDirsPsr4;

        }, null, ClassLoader::class);
    }
}