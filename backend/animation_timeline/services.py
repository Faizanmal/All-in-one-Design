"""
Services for Animation Timeline app.
"""
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone

from .models import (
    AnimationProject, AnimationComposition, AnimationLayer,
    AnimationTrack, AnimationKeyframe, LottieExport
)


class AnimationTimelineService:
    """
    Service for animation timeline operations.
    """
    
    def __init__(self, project: AnimationProject):
        self.project = project
    
    def get_timeline_data(
        self,
        composition: AnimationComposition,
        start_frame: int = 0,
        end_frame: Optional[int] = None,
        include_keyframes: bool = True,
    ) -> Dict[str, Any]:
        """Get timeline data for a composition."""
        if end_frame is None:
            end_frame = composition.duration_frames
        
        layers_data = []
        
        for layer in composition.layers.filter(is_shy=False).order_by('order'):
            layer_data = {
                'id': str(layer.id),
                'name': layer.name,
                'type': layer.layer_type,
                'in_point': layer.in_point,
                'out_point': layer.out_point,
                'is_visible': layer.is_visible,
                'is_locked': layer.is_locked,
                'is_solo': layer.is_solo,
                'color': layer.color,
                'transform': layer.transform,
                'opacity': layer.opacity,
                'blend_mode': layer.blend_mode,
            }
            
            if include_keyframes:
                tracks_data = []
                for track in layer.tracks.filter(is_muted=False):
                    keyframes = track.keyframes.filter(
                        frame_number__gte=start_frame,
                        frame_number__lte=end_frame
                    ).order_by('frame_number')
                    
                    tracks_data.append({
                        'id': str(track.id),
                        'property': track.property_path,
                        'type': track.property_type,
                        'color': track.color,
                        'keyframes': [
                            {
                                'id': str(kf.id),
                                'frame': kf.frame_number,
                                'value': kf.value,
                                'interpolation': kf.interpolation,
                                'bezier': kf.bezier_control_points,
                            }
                            for kf in keyframes
                        ]
                    })
                
                layer_data['tracks'] = tracks_data
            
            # Add effects
            effects_data = []
            for effect in layer.effects.filter(is_enabled=True).order_by('order'):
                effects_data.append({
                    'id': str(effect.id),
                    'type': effect.effect_type,
                    'parameters': effect.parameters,
                    'start_frame': effect.start_frame,
                    'end_frame': effect.end_frame,
                })
            layer_data['effects'] = effects_data
            
            layers_data.append(layer_data)
        
        return {
            'composition': {
                'id': str(composition.id),
                'name': composition.name,
                'width': composition.width,
                'height': composition.height,
                'frame_rate': composition.frame_rate,
                'duration': composition.duration_frames,
                'background': composition.background_color,
            },
            'layers': layers_data,
            'frame_range': {
                'start': start_frame,
                'end': end_frame,
            }
        }
    
    def duplicate_project(self, user) -> AnimationProject:
        """Duplicate the entire project."""
        with transaction.atomic():
            new_project = AnimationProject.objects.create(
                project=self.project.project,
                name=f"{self.project.name} (copy)",
                description=self.project.description,
                default_frame_rate=self.project.default_frame_rate,
                default_duration=self.project.default_duration,
                color_depth=self.project.color_depth,
                working_color_space=self.project.working_color_space,
                created_by=user,
            )
            
            # Duplicate compositions
            comp_map = {}
            for comp in self.project.compositions.all():
                new_comp = self._duplicate_composition_internal(comp, new_project)
                comp_map[comp.id] = new_comp
            
            return new_project
    
    def duplicate_composition(self, composition: AnimationComposition) -> AnimationComposition:
        """Duplicate a single composition."""
        return self._duplicate_composition_internal(composition, self.project)
    
    def _duplicate_composition_internal(
        self,
        composition: AnimationComposition,
        target_project: AnimationProject
    ) -> AnimationComposition:
        """Internal method to duplicate a composition."""
        with transaction.atomic():
            new_comp = AnimationComposition.objects.create(
                project=target_project,
                name=f"{composition.name} (copy)" if target_project == self.project else composition.name,
                description=composition.description,
                width=composition.width,
                height=composition.height,
                frame_rate=composition.frame_rate,
                duration_frames=composition.duration_frames,
                background_color=composition.background_color,
            )
            
            # Duplicate layers
            layer_map = {}
            for layer in composition.layers.order_by('order'):
                new_layer = self._duplicate_layer(layer, new_comp, layer_map)
                layer_map[layer.id] = new_layer
            
            # Update parent references
            for old_id, new_layer in layer_map.items():
                old_layer = AnimationLayer.objects.get(id=old_id)
                if old_layer.parent_layer and old_layer.parent_layer.id in layer_map:
                    new_layer.parent_layer = layer_map[old_layer.parent_layer.id]
                    new_layer.save()
            
            return new_comp
    
    def _duplicate_layer(
        self,
        layer: AnimationLayer,
        new_comp: AnimationComposition,
        layer_map: dict
    ) -> AnimationLayer:
        """Duplicate a layer and its tracks."""
        new_layer = AnimationLayer.objects.create(
            composition=new_comp,
            name=layer.name,
            layer_type=layer.layer_type,
            source_node_id=layer.source_node_id,
            in_point=layer.in_point,
            out_point=layer.out_point,
            start_frame=layer.start_frame,
            time_stretch=layer.time_stretch,
            is_visible=layer.is_visible,
            blend_mode=layer.blend_mode,
            opacity=layer.opacity,
            transform=layer.transform,
            mask_mode=layer.mask_mode,
            mask_data=layer.mask_data,
            order=layer.order,
            color=layer.color,
        )
        
        # Duplicate tracks
        for track in layer.tracks.all():
            new_track = AnimationTrack.objects.create(
                layer=new_layer,
                property_path=track.property_path,
                property_type=track.property_type,
                color=track.color,
            )
            
            # Duplicate keyframes
            for kf in track.keyframes.all():
                AnimationKeyframe.objects.create(
                    track=new_track,
                    frame_number=kf.frame_number,
                    time_ms=kf.time_ms,
                    value=kf.value,
                    interpolation=kf.interpolation,
                    easing_preset=kf.easing_preset,
                    bezier_control_points=kf.bezier_control_points,
                    spring_config=kf.spring_config,
                    is_hold=kf.is_hold,
                )
        
        # Duplicate effects
        for effect in layer.effects.all():
            from .models import AnimationEffect
            AnimationEffect.objects.create(
                layer=new_layer,
                effect_type=effect.effect_type,
                parameters=effect.parameters,
                start_frame=effect.start_frame,
                end_frame=effect.end_frame,
                is_enabled=effect.is_enabled,
                order=effect.order,
            )
        
        return new_layer


class LottieExporter:
    """
    Service for exporting animations to Lottie format.
    """
    
    def __init__(self, composition: AnimationComposition):
        self.composition = composition
    
    def export(
        self,
        created_by,
        format: str = 'json',
        include_assets: bool = True,
        optimize: bool = False,
        target_size: Optional[int] = None,
    ) -> LottieExport:
        """Create a Lottie export job."""
        # Get next version
        last_export = LottieExport.objects.filter(
            composition=self.composition
        ).order_by('-version').first()
        version = (last_export.version + 1) if last_export else 1
        
        export = LottieExport.objects.create(
            composition=self.composition,
            version=version,
            format=format,
            include_assets=include_assets,
            optimize=optimize,
            target_size=target_size,
            status='pending',
            created_by=created_by,
        )
        
        # Queue async export task
        from .tasks import export_lottie_task
        export_lottie_task.delay(str(export.id))
        
        return export
    
    def generate_lottie_json(self) -> Dict[str, Any]:
        """Generate Lottie JSON data."""
        lottie = {
            'v': '5.7.1',  # Lottie version
            'fr': self.composition.frame_rate,
            'ip': 0,
            'op': self.composition.duration_frames,
            'w': self.composition.width,
            'h': self.composition.height,
            'nm': self.composition.name,
            'ddd': 0,  # 3D disabled
            'assets': [],
            'layers': [],
        }
        
        # Convert layers
        for layer in self.composition.layers.filter(is_visible=True).order_by('-order'):
            lottie_layer = self._convert_layer(layer)
            lottie['layers'].append(lottie_layer)
        
        return lottie
    
    def _convert_layer(self, layer: AnimationLayer) -> Dict[str, Any]:
        """Convert a layer to Lottie format."""
        layer_type_map = {
            'shape': 4,
            'text': 5,
            'image': 2,
            'null': 3,
            'precomp': 0,
        }
        
        lottie_layer = {
            'ddd': 0,
            'ind': layer.order,
            'ty': layer_type_map.get(layer.layer_type, 4),
            'nm': layer.name,
            'sr': 1,
            'ks': self._convert_transform(layer),
            'ao': 0,
            'ip': layer.in_point,
            'op': layer.out_point,
            'st': layer.start_frame,
            'bm': 0,  # Blend mode
        }
        
        # Add parent reference
        if layer.parent_layer:
            lottie_layer['parent'] = layer.parent_layer.order
        
        return lottie_layer
    
    def _convert_transform(self, layer: AnimationLayer) -> Dict[str, Any]:
        """Convert transform with keyframes to Lottie format."""
        transform = layer.transform or {}
        
        ks = {
            'o': self._convert_property(layer, 'opacity', transform.get('opacity', 100)),
            'r': self._convert_property(layer, 'rotation', transform.get('rotation', 0)),
            'p': self._convert_property(layer, 'position', transform.get('position', [0, 0])),
            's': self._convert_property(layer, 'scale', transform.get('scale', [100, 100])),
            'a': {'a': 0, 'k': transform.get('anchor', [0, 0])},
        }
        
        return ks
    
    def _convert_property(
        self,
        layer: AnimationLayer,
        property_name: str,
        default_value
    ) -> Dict[str, Any]:
        """Convert an animated property with keyframes."""
        # Find track for this property
        track = layer.tracks.filter(property_path=property_name).first()
        
        if not track or not track.keyframes.exists():
            # Static value
            return {'a': 0, 'k': default_value}
        
        # Animated value
        keyframes = []
        for kf in track.keyframes.order_by('frame_number'):
            kf_data = {
                't': kf.frame_number,
                's': [kf.value] if not isinstance(kf.value, list) else kf.value,
            }
            
            if kf.bezier_control_points:
                bp = kf.bezier_control_points
                kf_data['o'] = {'x': [bp[0]], 'y': [bp[1]]}
                kf_data['i'] = {'x': [bp[2]], 'y': [bp[3]]}
            
            keyframes.append(kf_data)
        
        return {'a': 1, 'k': keyframes}
