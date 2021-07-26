use std::fs::File;

use rpt::*;

fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;

    let mut scene = Scene::new();

    scene.add(
        Object::new(
            load_obj(File::open("examples/simplestreet.obj")?)?
                .scale(&glm::vec3(0.01, 0.01, 0.01))
                .translate(&glm::vec3(0.0, -1.0, 0.0)),
        )
        .material(Material::specular(hex_color(0xF9E4B7), 0.1)),
    );
    scene.add(
        Object::new(plane(glm::vec3(0.0, 1.0, 0.0), -1.0))
            .material(Material::diffuse(hex_color(0x332F2C))),
    );

    scene.add(Light::Ambient(glm::vec3(0.1, 0.1, 0.1)));
    scene.add(Light::Point(
        glm::vec3(60.0, 60.0, 60.0),
        glm::vec3(-1.0, 2.0, 0.0),
    ));
    scene.add(Light::Point(
        glm::vec3(60.0, 60.0, 60.0),
        glm::vec3(1.0, 2.0, 0.0),
    ));

    Renderer::new(&scene, Camera::default())
        .width(800)
        .height(800)
        .render()
        .save("output.png")?;

    Ok(())
}
